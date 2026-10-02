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


def parse_options(name, args, allowed):
    """Отделить однобуквенные опции команды name от операндов.

    allowed - строка допустимых опций; опции можно объединять
    (-al) и указывать после операндов. Аргумент "--" завершает
    опции, "-" считается операндом. Неизвестная опция - ошибка.
    """
    options, operands = set(), []
    args = iter(args)
    for arg in args:
        if arg == "--":
            operands.extend(args)
            break
        if not arg.startswith("-") or arg == "-":
            operands.append(arg)
            continue
        for flag in arg[1:]:
            if flag not in allowed:
                raise CommandError(f"{name}: invalid option -- '{flag}'")
            options.add(flag)
    return options, operands


def format_entry(name, node, long_format):
    """Сформировать строку ls для одного файла или директории.

    В длинном формате выводятся тип (d - директория, - - файл),
    владелец, группа, размер файла в байтах и имя.
    """
    if not long_format:
        return name
    if isinstance(node, VfsDir):
        kind, size = "d", DIR_SIZE
    else:
        kind, size = "-", len(node.data)
    return f"{kind} {node.owner:<6} {node.group:<6} {size:>6} {name}"


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
    options, paths = parse_options("ls", args, LS_OPTIONS)
    paths = paths or ["."]
    errors = []
    files, dirs = find_nodes(shell, paths, errors)
    blocks = [format_listing(files, options | {"a"})] if files else []
    show_headers = bool(paths[1:])
    for path, node in dirs:
        listing = format_listing(sorted(node.children.items()), options)
        blocks.append(f"{path}:\n{listing}" if show_headers else listing)
    return finish("ls", "\n\n".join(blocks).rstrip("\n"), errors)


def read_texts(shell, name, paths, errors):
    """Прочитать содержимое файлов VFS как текст UTF-8.

    Для пустого списка путей выбрасывает CommandError (чтение
    стандартного ввода не поддерживается). Ненайденные пути и
    директории добавляются в errors.
    """
    if not paths:
        raise CommandError(f"{name}: missing file operand")
    texts = []
    for path in paths:
        try:
            node = shell.find(path)
        except VfsPathError as error:
            errors.append(f"{path}: {error}")
            continue
        if isinstance(node, VfsDir):
            errors.append(f"{path}: Is a directory")
            continue
        text = node.data.decode("utf-8", errors="replace")
        texts.append(text.replace("\r\n", "\n"))
    return texts


def cmd_cat(shell, args):
    """Вывести содержимое файлов, объединив их последовательно."""
    errors = []
    text = "".join(read_texts(shell, "cat", args, errors))
    if text.endswith("\n"):
        text = text[:-1]
    return finish("cat", text, errors)


def cmd_rev(shell, args):
    """Вывести строки файлов, переставив символы в обратном порядке."""
    errors = []
    lines = []
    for text in read_texts(shell, "rev", args, errors):
        lines.extend(line[::-1] for line in text.splitlines())
    return finish("rev", "\n".join(lines), errors)


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
