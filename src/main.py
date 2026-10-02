"""Точка входа эмулятора командной оболочки."""

import sys

from emulator.repl import run_repl
from emulator.shell import Shell


def main():
    """Запустить эмулятор в интерактивном режиме."""
    sys.exit(run_repl(Shell()))


if __name__ == "__main__":
    main()
