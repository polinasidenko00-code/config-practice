"""Команды для работы с файлами и директориями VFS."""

from emulator.errors import CommandError
from emulator.vfs import NOT_A_DIRECTORY, VfsDir, VfsPathError

MAX_CD_ARGS = 1
LS_OPTIONS = "al"
HIDDEN_PREFIX = "."
DIR_SIZE = "-"


def finish(name, output, errors):
    """Вернуть вывод или выбросить ошибку с частичным выводом.

    errors - список сообщений об ошибках для отдельных
    аргументов команды name.
    """
    if errors:
        raise CommandError(
            "\n".join(f"{name}: {error}" for error in errors), output
        )
    return output


def parse_ls_options(args):
    """Отделить опции ls (-a, -l, -al) от путей."""
    options, paths = set(), []
    for arg in args:
        if not arg.startswith("-") or arg == "-":
            paths.append(arg)
            continue
        for flag in arg[1:]:
            if flag not in LS_OPTIONS:
                raise CommandError(f"ls: invalid option -- '{flag}'")
            options.add(flag)
    return options, paths


def format_entry(name, node, long_format):
    """Сформировать строку ls для одного файла или директории.

    В длинном формате выводятся тип (d - директория, - - файл),
    размер файла в байтах и имя.
    """
    if not long_format:
        return name
    if isinstance(node, VfsDir):
        return f"d {DIR_SIZE:>8} {name}"
    return f"- {len(node.data):>8} {name}"


def format_listing(entries, options):
    """Сформировать вывод ls для списка пар (имя, узел)."""
    if "a" not in options:
        entries = [
            (name, node) for name, node in entries
            if not name.startswith(HIDDEN_PREFIX)
        ]
    lines = [format_entry(name, node, "l" in options)
             for name, node in entries]
    separator = "\n" if "l" in options else "  "
    return separator.join(lines)


def find_nodes(shell, paths, errors):
    """Найти узлы по путям; разделить на файлы и директории.

    Ненайденные пути добавляются в errors.
    """
    files, dirs = [], []
    for path in paths:
        try:
            node = shell.find(path)
        except VfsPathError as error:
            errors.append(f"cannot access '{path}': {error}")
            continue
        group = dirs if isinstance(node, VfsDir) else files
        group.append((path, node))
    return files, dirs


def cmd_ls(shell, args):
    """Вывести содержимое директорий или имена файлов.

    Без путей выводится текущая директория. -a показывает
    скрытые файлы (имя начинается с точки), -l - длинный
    формат. Для нескольких путей содержимое каждой директории
    выводится под заголовком "путь:".
    """
    options, paths = parse_ls_options(args)
    paths = paths or ["."]
    errors = []
    files, dirs = find_nodes(shell, paths, errors)
    blocks = [format_listing(files, options | {"a"})] if files else []
    show_headers = bool(paths[1:])
    for path, node in dirs:
        listing = format_listing(sorted(node.children.items()), options)
        blocks.append(f"{path}:\n{listing}" if show_headers else listing)
    return finish("ls", "\n\n".join(blocks).rstrip("\n"), errors)


def cmd_cd(shell, args):
    """Сменить текущую директорию; без аргумента - в корень (~)."""
    if len(args) > MAX_CD_ARGS:
        raise CommandError("cd: too many arguments")
    target = args[0] if args else "~"
    parts = shell.resolve(target)
    try:
        node = shell.vfs.get(parts)
    except VfsPathError as error:
        raise CommandError(f"cd: {target}: {error}") from None
    if not isinstance(node, VfsDir):
        raise CommandError(f"cd: {target}: {NOT_A_DIRECTORY}")
    shell.cwd = parts
    return ""
