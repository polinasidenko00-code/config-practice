"""Интерактивный цикл чтения-выполнения-вывода (REPL)."""

import sys

from emulator.commands import CommandError


def execute_line(shell, line, out, err):
    """Выполнить одну строку и напечатать вывод или ошибку.

    Ошибка выполнения команды печатается в err (после частичного
    вывода команды, если он есть) и не прерывает работу эмулятора.
    """
    try:
        output = shell.execute(line)
    except CommandError as error:
        if error.output:
            print(error.output, file=out)
        out.flush()
        print(error, file=err)
        err.flush()
        return
    if output:
        print(output, file=out)


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
        execute_line(shell, line, out, err)
    return shell.exit_code
