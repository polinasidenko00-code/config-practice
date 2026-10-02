"""Точка входа эмулятора командной оболочки."""

import sys

from emulator.config import (
    create_vfs,
    format_config,
    format_vfs_info,
    parse_args,
)
from emulator.repl import run_repl
from emulator.script import ScriptError, read_script, run_script
from emulator.shell import Shell
from emulator.vfs import VfsError

LOAD_ERROR_CODE = 1


def main(argv=None):
    """Запустить эмулятор с параметрами командной строки.

    Загружает VFS и стартовый скрипт; при ошибке загрузки
    сообщает о ней и возвращает код 1. Затем выполняет
    команды скрипта и, если скрипт не вызвал exit, запускает
    интерактивный режим. Возвращает код завершения.
    """
    args = parse_args(argv)
    print(format_config(args))
    try:
        vfs = create_vfs(args)
        lines = read_script(args.script) if args.script else []
    except (VfsError, ScriptError) as error:
        sys.stdout.flush()
        print(error, file=sys.stderr)
        return LOAD_ERROR_CODE
    print(format_vfs_info(vfs))
    shell = Shell(vfs)
    run_script(shell, lines, sys.stdout, sys.stderr)
    if shell.running:
        run_repl(shell)
    return shell.exit_code


if __name__ == "__main__":
    sys.exit(main())
