"""Виртуальная файловая система (VFS), хранящаяся в памяти.

Источником VFS является директория на диске пользователя. При
загрузке вся структура директорий и содержимое файлов читаются
в память; дальнейшие операции выполняются только с памятью,
исходные данные на диске не изменяются.
"""

import os

DEFAULT_VFS_NAME = "vfs"


class VfsError(Exception):
    """Ошибка загрузки или сохранения VFS."""


class VfsFile:
    """Файл VFS: имя и содержимое в виде байтов."""

    def __init__(self, name, data=b""):
        """Создать файл с указанным именем и содержимым."""
        self.name = name
        self.data = data


class VfsDir:
    """Директория VFS: имя и словарь дочерних узлов по именам."""

    def __init__(self, name):
        """Создать пустую директорию с указанным именем."""
        self.name = name
        self.children = {}

    def add(self, node):
        """Добавить дочерний файл или директорию."""
        self.children[node.name] = node


class Vfs:
    """Виртуальная файловая система: имя и корневая директория."""

    def __init__(self, name=DEFAULT_VFS_NAME, root=None):
        """Создать VFS; без корня создается пустая VFS."""
        self.name = name
        self.root = root if root is not None else VfsDir("")

    def count(self):
        """Вернуть (число директорий, число файлов) без корня."""
        dirs, files = 0, 0
        stack = [self.root]
        while stack:
            directory = stack.pop()
            for node in directory.children.values():
                if isinstance(node, VfsDir):
                    dirs += 1
                    stack.append(node)
                else:
                    files += 1
        return dirs, files


def load_vfs(path, name=DEFAULT_VFS_NAME):
    """Загрузить VFS из директории на диске в память.

    Выбрасывает VfsError, если путь не существует, не является
    директорией, содержит неподдерживаемые файлы (ссылки,
    устройства) или не может быть прочитан.
    """
    prefix = f"emulator: cannot load VFS '{path}'"
    if not os.path.exists(path):
        raise VfsError(f"{prefix}: no such file or directory")
    if not os.path.isdir(path):
        raise VfsError(f"{prefix}: invalid format, not a directory")
    root = VfsDir("")
    try:
        _load_dir(path, root)
    except OSError as error:
        raise VfsError(
            f"{prefix}: {error.filename or path}: {error.strerror}"
        ) from None
    return Vfs(name, root)


def _load_dir(path, directory):
    """Рекурсивно прочитать содержимое директории в узел VFS."""
    with os.scandir(path) as entries:
        for entry in sorted(entries, key=lambda item: item.name):
            directory.add(_load_node(entry))


def _load_node(entry):
    """Прочитать один элемент директории в узел VFS."""
    if entry.is_dir(follow_symlinks=False):
        directory = VfsDir(entry.name)
        _load_dir(entry.path, directory)
        return directory
    if entry.is_file(follow_symlinks=False):
        with open(entry.path, "rb") as file:
            return VfsFile(entry.name, file.read())
    raise VfsError(
        f"emulator: cannot load VFS: '{entry.path}': "
        "invalid format, unsupported file type"
    )


def save_vfs(vfs, path):
    """Сохранить VFS на диск в исходном формате - в директорию.

    Директория назначения создается; если она уже существует,
    то должна быть пустой. Выбрасывает VfsError при ошибке.
    """
    _check_destination(path)
    try:
        os.makedirs(path, exist_ok=True)
        _save_dir(vfs.root, path)
    except OSError as error:
        raise VfsError(
            f"vfs-save: cannot write '{error.filename or path}': "
            f"{error.strerror}"
        ) from None


def _check_destination(path):
    """Проверить, что путь свободен или является пустой папкой."""
    if not os.path.exists(path):
        return
    if not os.path.isdir(path):
        raise VfsError(f"vfs-save: '{path}': not a directory")
    if os.listdir(path):
        raise VfsError(f"vfs-save: '{path}': directory is not empty")


def _save_dir(directory, path):
    """Рекурсивно записать узел-директорию VFS на диск."""
    for node in directory.children.values():
        target = os.path.join(path, node.name)
        if isinstance(node, VfsDir):
            os.mkdir(target)
            _save_dir(node, target)
        else:
            with open(target, "wb") as file:
                file.write(node.data)
