"""Точка входа эмулятора командной оболочки."""

import sys

from emulator.config import format_config, parse_args, vfs_name_from_path
from emulator.repl import run_repl
from emulator.script import ScriptError, read_script, run_script
from emulator.shell import Shell

SCRIPT_ERROR_CODE = 1


def main(argv=None):
    """Запустить эмулятор с параметрами командной строки.

    Если задан стартовый скрипт, сначала выполняются его
    команды; затем, если скрипт не вызвал exit, запускается
    интерактивный режим. Возвращает код завершения.
    """
    args = parse_args(argv)
    print(format_config(args))
    shell = Shell(vfs_name_from_path(args.vfs))
    if args.script:
        try:
            lines = read_script(args.script)
        except ScriptError as error:
            sys.stdout.flush()
            print(error, file=sys.stderr)
            return SCRIPT_ERROR_CODE
        run_script(shell, lines, sys.stdout, sys.stderr)
    if shell.running:
        run_repl(shell)
    return shell.exit_code


if __name__ == "__main__":
    sys.exit(main())
