"""Интерактивный цикл чтения-выполнения-вывода (REPL)."""

import sys

from emulator.commands import CommandError


def run_repl(shell, read=input, out=None, err=None):
    """Запустить диалог с пользователем до команды exit или EOF.

    read - функция чтения строки с приглашением, out и err -
    потоки для обычного вывода и сообщений об ошибках.
    Возвращает код завершения эмулятора.
    """
    out = out or sys.stdout
    err = err or sys.stderr
    while shell.running:
        try:
            line = read(shell.prompt)
        except EOFError:
            print(file=out)
            break
        except KeyboardInterrupt:
            print("^C", file=out)
            continue
        try:
            output = shell.execute(line)
        except CommandError as error:
            print(error, file=err)
            continue
        if output:
            print(output, file=out)
    return shell.exit_code
