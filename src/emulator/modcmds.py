"""Команды, изменяющие VFS: chown и rm.

Все изменения выполняются только в памяти; данные VFS на
диске не меняются (сохранить состояние можно командой vfs-save).
"""

import re

from emulator.errors import CommandError
from emulator.filecmds import finish, parse_options
from emulator.vfs import (
    NO_SUCH_FILE,
    SEPARATOR,
    VfsDir,
    VfsPathError,
    walk,
)

CHOWN_OPTIONS = "Rv"
RM_OPTIONS = "rRfv"
OWNER_SEPARATOR = ":"
NAME_PATTERN = re.compile(r"[A-Za-z_][A-Za-z0-9_.-]*\Z")
PROTECTED_NAMES = (".", "..")


class OperandError(Exception):
    """Ошибка обработки одного операнда команды."""


def parse_owner(spec):
    """Разобрать OWNER, OWNER:GROUP, OWNER: или :GROUP.

    Возвращает пару (владелец, группа), где None означает
    "не изменять". Имя должно начинаться с буквы или _ и
    состоять из букв, цифр, _, . и -.
    """
    owner, _separator, group = spec.partition(OWNER_SEPARATOR)
    if not owner and not group:
        raise CommandError(f"chown: invalid spec: '{spec}'")
    if owner and not NAME_PATTERN.match(owner):
        raise CommandError(f"chown: invalid user: '{spec}'")
    if group and not NAME_PATTERN.match(group):
        raise CommandError(f"chown: invalid group: '{spec}'")
    return owner or None, group or None


def change_owner(path, node, owner, group):
    """Сменить владельца и группу узла; вернуть сообщение для -v."""
    old = f"{node.owner}:{node.group}"
    node.owner = owner or node.owner
    node.group = group or node.group
    new = f"{node.owner}:{node.group}"
    if old == new:
        return f"ownership of '{path}' retained as {new}"
    return f"changed ownership of '{path}' from {old} to {new}"


def cmd_chown(shell, args):
    """Сменить владельца и/или группу файлов и директорий.

    chown [-R] [-v] OWNER[:GROUP] PATH... ; -R - рекурсивно для
    всего содержимого директорий, -v - сообщать о каждом узле.
    Ненайденные пути сообщаются, остальные обрабатываются.
    """
    options, operands = parse_options("chown", args, CHOWN_OPTIONS)
    if not operands:
        raise CommandError("chown: missing operand")
    spec, paths = operands[0], operands[1:]
    if not paths:
        raise CommandError(f"chown: missing operand after '{spec}'")
    owner, group = parse_owner(spec)
    messages, errors = [], []
    for path in paths:
        try:
            node = shell.find(path)
        except VfsPathError as error:
            errors.append(f"cannot access '{path}': {error}")
            continue
        targets = walk(path, node) if "R" in options else [(path, node)]
        messages.extend(
            change_owner(item_path, item, owner, group)
            for item_path, item in targets
        )
    output = "\n".join(messages) if "v" in options else ""
    return finish("chown", output, errors)


def check_removable(shell, path, recursive):
    """Проверить операнд rm и вернуть (компоненты пути, узел).

    Выбрасывает VfsPathError, если путь не найден, и
    OperandError, если удалять нельзя: последний компонент
    "." или "..", директория без -r, корень VFS.
    """
    last = path.rstrip(SEPARATOR).split(SEPARATOR)[-1]
    if last in PROTECTED_NAMES:
        raise OperandError(
            "refusing to remove '.' or '..' directory: "
            f"skipping '{path}'"
        )
    parts = shell.resolve(path)
    node = shell.vfs.get(parts)
    if isinstance(node, VfsDir) and not recursive:
        raise OperandError(f"cannot remove '{path}': Is a directory")
    if not parts:
        raise OperandError(
            f"it is dangerous to operate recursively on '{path}'"
        )
    return parts, node


def removed_messages(path, node):
    """Сообщения -v об удалении узла: потомки перед родителями."""
    return [
        f"removed directory '{item_path}'" if isinstance(item, VfsDir)
        else f"removed '{item_path}'"
        for item_path, item in reversed(list(walk(path, node)))
    ]


def cmd_rm(shell, args):
    """Удалить файлы и директории из VFS в памяти.

    rm [-r|-R] [-f] [-v] PATH... ; -r - удалять директории
    вместе с содержимым, -f - не сообщать об отсутствующих
    путях и об отсутствии операндов, -v - сообщать о каждом
    удаленном узле.
    """
    options, paths = parse_options("rm", args, RM_OPTIONS)
    recursive = bool(options & {"r", "R"})
    force = "f" in options
    if not paths and not force:
        raise CommandError("rm: missing operand")
    messages, errors = [], []
    for path in paths:
        try:
            parts, node = check_removable(shell, path, recursive)
        except VfsPathError as error:
            if not (force and str(error) == NO_SUCH_FILE):
                errors.append(f"cannot remove '{path}': {error}")
            continue
        except OperandError as error:
            errors.append(str(error))
            continue
        shell.vfs.remove(parts)
        messages.extend(removed_messages(path, node))
    output = "\n".join(messages) if "v" in options else ""
    return finish("rm", output, errors)
