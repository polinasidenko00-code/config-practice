"""Разбор параметров командной строки эмулятора."""

import argparse
import os

from emulator.shell import DEFAULT_VFS_NAME


def build_parser():
    """Создать парсер параметров командной строки."""
    parser = argparse.ArgumentParser(
        prog="emulator",
        description="Shell emulator of a UNIX-like OS.",
    )
    parser.add_argument(
        "--vfs", metavar="PATH",
        help="path to the physical location of the VFS",
    )
    parser.add_argument(
        "--script", metavar="PATH",
        help="path to the startup script",
    )
    return parser


def parse_args(argv=None):
    """Разобрать параметры командной строки.

    argv - список аргументов; None означает sys.argv[1:].
    """
    return build_parser().parse_args(argv)


def vfs_name_from_path(path):
    """Получить имя VFS для приглашения из пути к ней.

    Имя - последний компонент пути. Если путь не задан или
    не содержит имени (например, корень диска), используется
    имя по умолчанию.
    """
    if not path:
        return DEFAULT_VFS_NAME
    name = os.path.basename(os.path.normpath(path))
    return name or DEFAULT_VFS_NAME


def format_config(args):
    """Сформировать отладочный вывод всех заданных параметров."""
    return "\n".join([
        "[debug] emulator parameters:",
        f"[debug]   vfs    = {args.vfs}",
        f"[debug]   script = {args.script}",
    ])
