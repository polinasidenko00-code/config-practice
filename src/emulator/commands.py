"""Команды эмулятора.

Каждая команда - функция (shell, args), возвращающая вывод
в виде строки. На текущем этапе ls и cd являются заглушками:
они только выводят свое имя и полученные аргументы.
"""

MAX_CD_ARGS = 1
MAX_EXIT_ARGS = 1


class CommandError(Exception):
    """Ошибка выполнения команды (неверные аргументы и т.п.)."""


class ExitRequest(Exception):
    """Запрос на завершение работы эмулятора с кодом возврата."""

    def __init__(self, code):
        """Сохранить код возврата для завершения эмулятора."""
        super().__init__(code)
        self.code = code


def format_stub(name, args):
    """Сформировать вывод команды-заглушки: имя и аргументы."""
    return f"{name}: args={args}"


def cmd_ls(_shell, args):
    """Заглушка ls: принимает любое число аргументов."""
    return format_stub("ls", args)


def cmd_cd(_shell, args):
    """Заглушка cd: принимает не более одного аргумента."""
    if len(args) > MAX_CD_ARGS:
        raise CommandError("cd: too many arguments")
    return format_stub("cd", args)


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


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
}
