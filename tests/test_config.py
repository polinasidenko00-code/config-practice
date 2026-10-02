"""Тесты разбора параметров командной строки."""

import contextlib
import io
import os
import sys
import unittest

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), os.pardir, "src")
)

from emulator.config import (  # noqa: E402
    format_config,
    parse_args,
    vfs_name_from_path,
)


class ParseArgsTest(unittest.TestCase):
    """Проверка разбора параметров."""

    def test_defaults(self):
        """Без параметров оба пути не заданы."""
        args = parse_args([])
        self.assertIsNone(args.vfs)
        self.assertIsNone(args.script)

    def test_all_parameters(self):
        """Оба параметра сохраняются."""
        args = parse_args(["--vfs", "data/vfs", "--script", "s.txt"])
        self.assertEqual(args.vfs, "data/vfs")
        self.assertEqual(args.script, "s.txt")

    def test_unknown_parameter(self):
        """Неизвестный параметр завершает работу с ошибкой."""
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                parse_args(["--bad"])


class VfsNameTest(unittest.TestCase):
    """Проверка получения имени VFS из пути."""

    def test_no_path(self):
        """Без пути используется имя по умолчанию."""
        self.assertEqual(vfs_name_from_path(None), "vfs")

    def test_last_component(self):
        """Имя - последний компонент пути."""
        self.assertEqual(vfs_name_from_path("data/my_vfs"), "my_vfs")

    def test_trailing_separator(self):
        """Завершающий разделитель пути игнорируется."""
        self.assertEqual(vfs_name_from_path("data/my_vfs/"), "my_vfs")

    def test_root(self):
        """Для корня используется имя по умолчанию."""
        self.assertEqual(vfs_name_from_path("/"), "vfs")


class FormatConfigTest(unittest.TestCase):
    """Проверка отладочного вывода параметров."""

    def test_all_parameters_printed(self):
        """В выводе есть значения всех параметров."""
        text = format_config(parse_args(["--vfs", "a", "--script", "b"]))
        self.assertIn("vfs    = a", text)
        self.assertIn("script = b", text)


if __name__ == "__main__":
    unittest.main()
