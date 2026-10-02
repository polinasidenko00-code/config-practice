"""Выполнение стартового скрипта эмулятора."""

from emulator.repl import execute_line

COMMENT_PREFIX = "#"


class ScriptError(Exception):
    """Ошибка загрузки стартового скрипта."""


def read_script(path):
    """Прочитать строки стартового скрипта из файла.

    Выбрасывает ScriptError, если файл не найден, недоступен
    или не является текстом в кодировке UTF-8.
    """
    try:
        with open(path, encoding="utf-8-sig") as file:
            return file.read().splitlines()
    except OSError as error:
        raise ScriptError(
            f"emulator: cannot read script '{path}': {error.strerror}"
        ) from None
    except UnicodeDecodeError:
        raise ScriptError(
            f"emulator: script '{path}' is not a UTF-8 text file"
        ) from None


def is_skipped(line):
    """Проверить, что строка пустая или является комментарием."""
    stripped = line.strip()
    return not stripped or stripped.startswith(COMMENT_PREFIX)


def run_script(shell, lines, out, err):
    """Выполнить команды скрипта последовательно.

    Перед выполнением каждая команда печатается вместе с
    приглашением, имитируя диалог с пользователем. Строки с
    ошибками пропускаются, выполнение продолжается. Команда
    exit останавливает скрипт.
    """
    for line in lines:
        if not shell.running:
            break
        if is_skipped(line):
            continue
        print(shell.prompt + line, file=out)
        execute_line(shell, line, out, err)
