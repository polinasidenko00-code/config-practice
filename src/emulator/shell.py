"""Ядро эмулятора: состояние оболочки и выполнение команд."""

from emulator.commands import COMMANDS, CommandError, ExitRequest
from emulator.parser import parse
from emulator.vfs import Vfs


class Shell:
    """Состояние эмулятора оболочки."""

    def __init__(self, vfs=None):
        """Создать оболочку для VFS; без VFS создается пустая."""
        self.vfs = vfs if vfs is not None else Vfs()
        self.running = True
        self.exit_code = 0

    @property
    def prompt(self):
        """Приглашение к вводу, содержащее имя VFS."""
        return f"{self.vfs.name}:~$ "

    def execute(self, line):
        """Выполнить строку ввода и вернуть вывод команды.

        Для пустой строки возвращает пустую строку.
        Выбрасывает CommandError при неизвестной команде
        или неверных аргументах.
        """
        name, args = parse(line)
        if name is None:
            return ""
        handler = COMMANDS.get(name)
        if handler is None:
            raise CommandError(f"{name}: command not found")
        try:
            return handler(self, args)
        except ExitRequest as request:
            self.running = False
            self.exit_code = request.code
            return ""
