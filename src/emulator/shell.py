"""Ядро эмулятора: состояние оболочки и выполнение команд."""

from emulator.commands import COMMANDS, CommandError, ExitRequest
from emulator.parser import parse
from emulator.vfs import Vfs, format_path, split_path


class Shell:
    """Состояние эмулятора: VFS, текущая директория, история."""

    def __init__(self, vfs=None):
        """Создать оболочку для VFS; без VFS создается пустая."""
        self.vfs = vfs if vfs is not None else Vfs()
        self.cwd = []
        self.history = []
        self.running = True
        self.exit_code = 0

    @property
    def prompt(self):
        """Приглашение к вводу: имя VFS и текущая директория."""
        return f"{self.vfs.name}:{format_path(self.cwd)}$ "

    def resolve(self, path):
        """Получить компоненты абсолютного пути относительно cwd."""
        return split_path(path, self.cwd)

    def find(self, path):
        """Найти узел VFS по пути; VfsPathError, если его нет."""
        return self.vfs.get(self.resolve(path))

    def execute(self, line):
        """Выполнить строку ввода и вернуть вывод команды.

        Непустая строка добавляется в историю команд. Для пустой
        строки возвращает пустую строку. Выбрасывает CommandError
        при неизвестной команде или ошибке ее выполнения.
        """
        name, args = parse(line)
        if name is None:
            return ""
        self.history.append(line.strip())
        handler = COMMANDS.get(name)
        if handler is None:
            raise CommandError(f"{name}: command not found")
        try:
            return handler(self, args)
        except ExitRequest as request:
            self.running = False
            self.exit_code = request.code
            return ""
