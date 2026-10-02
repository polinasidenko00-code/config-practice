"""Ядро эмулятора: состояние оболочки и выполнение команд."""

from emulator.commands import COMMANDS, CommandError, ExitRequest
from emulator.parser import parse

DEFAULT_VFS_NAME = "vfs"


class Shell:
    """Состояние эмулятора оболочки."""

    def __init__(self, vfs_name=DEFAULT_VFS_NAME):
        """Создать оболочку, работающую с VFS с указанным именем."""
        self.vfs_name = vfs_name
        self.running = True
        self.exit_code = 0

    @property
    def prompt(self):
        """Приглашение к вводу, содержащее имя VFS."""
        return f"{self.vfs_name}:~$ "

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
            return handler(args)
        except ExitRequest as request:
            self.running = False
            self.exit_code = request.code
            return ""
