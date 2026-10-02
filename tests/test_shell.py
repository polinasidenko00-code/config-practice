"""Тесты команд, оболочки и REPL."""

import io
import os
import sys
import unittest

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), os.pardir, "src")
)

from emulator.commands import CommandError  # noqa: E402
from emulator.repl import run_repl  # noqa: E402
from emulator.shell import Shell  # noqa: E402


def fake_input(lines):
    """Создать функцию чтения, выдающую строки из списка."""
    iterator = iter(lines)

    def read(_prompt):
        """Вернуть следующую строку или выбросить EOFError."""
        try:
            return next(iterator)
        except StopIteration:
            raise EOFError from None

    return read


class ShellTest(unittest.TestCase):
    """Проверка выполнения команд оболочкой."""

    def setUp(self):
        """Создать новую оболочку для каждого теста."""
        self.shell = Shell("myvfs")

    def test_prompt_contains_vfs_name(self):
        """Приглашение содержит имя VFS."""
        self.assertIn("myvfs", self.shell.prompt)

    def test_ls_stub(self):
        """ls выводит свое имя и аргументы."""
        output = self.shell.execute("ls -l /home")
        self.assertEqual(output, "ls: args=['-l', '/home']")

    def test_cd_stub(self):
        """cd выводит свое имя и аргумент."""
        self.assertEqual(self.shell.execute("cd /tmp"), "cd: args=['/tmp']")

    def test_cd_too_many_args(self):
        """cd с двумя аргументами - ошибка."""
        with self.assertRaises(CommandError):
            self.shell.execute("cd a b")

    def test_unknown_command(self):
        """Неизвестная команда - ошибка."""
        with self.assertRaisesRegex(CommandError, "command not found"):
            self.shell.execute("foo")

    def test_empty_line(self):
        """Пустая строка ничего не выводит."""
        self.assertEqual(self.shell.execute(""), "")

    def test_exit(self):
        """exit останавливает оболочку с кодом 0."""
        self.shell.execute("exit")
        self.assertFalse(self.shell.running)
        self.assertEqual(self.shell.exit_code, 0)

    def test_exit_with_code(self):
        """exit N завершает работу с кодом N."""
        self.shell.execute("exit 3")
        self.assertEqual(self.shell.exit_code, 3)

    def test_exit_bad_args(self):
        """exit с нечисловым или лишним аргументом - ошибка."""
        for line in ("exit abc", "exit 1 2"):
            with self.assertRaises(CommandError):
                self.shell.execute(line)
        self.assertTrue(self.shell.running)


class ReplTest(unittest.TestCase):
    """Проверка интерактивного цикла."""

    def run_lines(self, lines):
        """Прогнать строки через REPL, вернуть (код, вывод, ошибки)."""
        out, err = io.StringIO(), io.StringIO()
        code = run_repl(Shell(), fake_input(lines), out, err)
        return code, out.getvalue(), err.getvalue()

    def test_dialog(self):
        """Ошибки не прерывают диалог, exit завершает его."""
        code, out, err = self.run_lines(
            ["ls", "bad", "cd x y", "exit 2", "ls never"]
        )
        self.assertEqual(code, 2)
        self.assertIn("ls: args=[]", out)
        self.assertNotIn("never", out)
        self.assertIn("bad: command not found", err)
        self.assertIn("cd: too many arguments", err)

    def test_eof_stops_repl(self):
        """Конец ввода завершает работу с кодом 0."""
        code, _out, _err = self.run_lines(["ls"])
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
