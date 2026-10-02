"""Тесты выполнения стартового скрипта и точки входа."""

import contextlib
import io
import os
import sys
import tempfile
import unittest

SRC_DIR = os.path.join(os.path.dirname(__file__), os.pardir, "src")
sys.path.insert(0, SRC_DIR)

from emulator.script import ScriptError, read_script, run_script  # noqa
from emulator.shell import Shell  # noqa: E402
from main import main  # noqa: E402


def write_temp_script(text):
    """Записать текст во временный файл и вернуть путь к нему."""
    file = tempfile.NamedTemporaryFile(
        "w", suffix=".txt", delete=False, encoding="utf-8"
    )
    with file:
        file.write(text)
    return file.name


class RunScriptTest(unittest.TestCase):
    """Проверка последовательного выполнения команд скрипта."""

    def run_lines(self, lines):
        """Выполнить строки, вернуть (оболочка, вывод, ошибки)."""
        shell = Shell("test")
        out, err = io.StringIO(), io.StringIO()
        run_script(shell, lines, out, err)
        return shell, out.getvalue(), err.getvalue()

    def test_input_and_output_echoed(self):
        """Печатаются приглашение, команда и ее вывод."""
        _shell, out, _err = self.run_lines(["ls /home"])
        self.assertEqual(out, "test:~$ ls /home\nls: args=['/home']\n")

    def test_errors_skipped(self):
        """Ошибочные строки пропускаются, выполнение продолжается."""
        shell, out, err = self.run_lines(["bad", "cd a b", "ls ok"])
        self.assertIn("bad: command not found", err)
        self.assertIn("cd: too many arguments", err)
        self.assertIn("ls: args=['ok']", out)
        self.assertTrue(shell.running)

    def test_comments_and_empty_lines(self):
        """Комментарии и пустые строки не выполняются."""
        _shell, out, err = self.run_lines(["# ls", "", "   "])
        self.assertEqual((out, err), ("", ""))

    def test_exit_stops_script(self):
        """exit останавливает выполнение скрипта."""
        shell, out, _err = self.run_lines(["exit 5", "ls never"])
        self.assertFalse(shell.running)
        self.assertEqual(shell.exit_code, 5)
        self.assertNotIn("never", out)


class ReadScriptTest(unittest.TestCase):
    """Проверка чтения файла скрипта."""

    def test_missing_file(self):
        """Отсутствующий файл - ошибка ScriptError."""
        with self.assertRaises(ScriptError):
            read_script("no_such_script.txt")

    def test_bom_removed(self):
        """BOM в начале файла не попадает в команду."""
        path = write_temp_script("﻿ls\n")
        self.addCleanup(os.remove, path)
        self.assertEqual(read_script(path), ["ls"])


class MainTest(unittest.TestCase):
    """Проверка точки входа с параметрами командной строки."""

    def run_main(self, argv):
        """Запустить main, вернуть (код, вывод, ошибки)."""
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out):
            with contextlib.redirect_stderr(err):
                code = main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_script_with_vfs(self):
        """Параметры выводятся, имя VFS попадает в приглашение."""
        path = write_temp_script("ls\nexit 4\n")
        self.addCleanup(os.remove, path)
        code, out, _err = self.run_main(
            ["--vfs", "disk/myfs", "--script", path]
        )
        self.assertEqual(code, 4)
        self.assertIn("vfs    = disk/myfs", out)
        self.assertIn("myfs:~$ ls", out)

    def test_missing_script(self):
        """Отсутствующий скрипт - код возврата 1."""
        code, _out, err = self.run_main(["--script", "no_such.txt"])
        self.assertEqual(code, 1)
        self.assertIn("cannot read script", err)


if __name__ == "__main__":
    unittest.main()
