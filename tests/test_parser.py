"""Тесты парсера строки ввода."""

import os
import sys
import unittest

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), os.pardir, "src")
)

from emulator.parser import parse  # noqa: E402


class ParseTest(unittest.TestCase):
    """Проверка разделения ввода на команду и аргументы."""

    def test_command_without_args(self):
        """Команда без аргументов."""
        self.assertEqual(parse("ls"), ("ls", []))

    def test_command_with_args(self):
        """Аргументы отделяются пробелами."""
        self.assertEqual(parse("ls -l /home"), ("ls", ["-l", "/home"]))

    def test_extra_spaces(self):
        """Лишние пробелы и табуляции игнорируются."""
        self.assertEqual(parse("  cd \t /tmp  "), ("cd", ["/tmp"]))

    def test_empty_line(self):
        """Пустая строка не содержит команды."""
        self.assertEqual(parse("   "), (None, []))


if __name__ == "__main__":
    unittest.main()
