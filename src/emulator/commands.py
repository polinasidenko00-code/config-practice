"""Реестр команд эмулятора и служебные команды.

Каждая команда - функция (shell, args), возвращающая вывод
в виде строки. Команды работы с файлами находятся в модуле
filecmds; служебная команда vfs-save сохраняет VFS на диск.
"""

from emulator.errors import CommandError, ExitRequest
from emulator.filecmds import cmd_cd, cmd_ls
from emulator.vfs import VfsError, save_vfs

__all__ = ["COMMANDS", "CommandError", "ExitRequest"]

MAX_EXIT_ARGS = 1
VFS_SAVE_ARGS = 1


def cmd_exit(_shell, args):
    """Завершить работу эмулятора.

    Необязательный аргумент - целочисленный код возврата.
    """
    if len(args) > MAX_EXIT_ARGS:
        raise CommandError("exit: too many arguments")
    code = 0
    if args:
        try:
            code = int(args[0])
        except ValueError:
            raise CommandError(
                f"exit: {args[0]}: numeric argument required"
            ) from None
    raise ExitRequest(code)


def cmd_vfs_save(shell, args):
    """Сохранить текущее состояние VFS на диск по указанному пути.

    Служебная команда: единственный аргумент - путь к новой или
    пустой директории реальной ОС.
    """
    if len(args) != VFS_SAVE_ARGS:
        raise CommandError("vfs-save: usage: vfs-save PATH")
    try:
        save_vfs(shell.vfs, args[0])
    except VfsError as error:
        raise CommandError(str(error)) from None
    return f"vfs-save: VFS '{shell.vfs.name}' saved to '{args[0]}'"


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
    "vfs-save": cmd_vfs_save,
}
