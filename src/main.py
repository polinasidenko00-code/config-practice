"""Точка входа эмулятора командной оболочки."""

import sys

from emulator.config import format_config, parse_args, vfs_name_from_path
from emulator.repl import run_repl
from emulator.shell import Shell


def main(argv=None):
    """Запустить эмулятор с параметрами командной строки.

    Возвращает код завершения эмулятора.
    """
    args = parse_args(argv)
    print(format_config(args))
    shell = Shell(vfs_name_from_path(args.vfs))
    return run_repl(shell)


if __name__ == "__main__":
    sys.exit(main())
