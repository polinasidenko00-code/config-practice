"""Тесты команд этапа 4: ls, cd, cat, rev, history."""

import os
import sys
import unittest

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), os.pardir, "src")
)

from emulator.commands import CommandError  # noqa: E402
from emulator.shell import Shell  # noqa: E402
from emulator.vfs import (  # noqa: E402
    Vfs,
    VfsDir,
    VfsFile,
    format_path,
    split_path,
)


def make_shell():
    """Создать оболочку с VFS из трех уровней.

    /
      a.txt          "one\\ntwo\\n"
      .hidden        ""
      home/
        user/
          notes.txt  "привет\\r\\n"
          bin.dat    b"\\xff"
        empty/
    """
    user = VfsDir("user")
    user.add(VfsFile("notes.txt", "привет\r\n".encode("utf-8")))
    user.add(VfsFile("bin.dat", b"\xff"))
    home = VfsDir("home")
    home.add(user)
    home.add(VfsDir("empty"))
    vfs = Vfs("t")
    for node in (VfsFile("a.txt", b"one\ntwo\n"), VfsFile(".hidden"),
                 home):
        vfs.root.add(node)
    return Shell(vfs)


class PathTest(unittest.TestCase):
    """Проверка разбора путей VFS."""

    def test_absolute_and_relative(self):
        """Абсолютный путь не зависит от cwd, относительный - да."""
        self.assertEqual(split_path("/a/b", ["x"]), ["a", "b"])
        self.assertEqual(split_path("a/b", ["x"]), ["x", "a", "b"])

    def test_dots(self):
        """. пропускается, .. поднимается, выше корня - корень."""
        self.assertEqual(split_path("./a/../b", ["x"]), ["x", "b"])
        self.assertEqual(split_path("../../..", ["x"]), [])

    def test_home(self):
        """~ - корень VFS."""
        self.assertEqual(split_path("~", ["x"]), [])
        self.assertEqual(split_path("~/a", ["x"]), ["a"])

    def test_format_path(self):
        """Компоненты превращаются в абсолютный путь."""
        self.assertEqual(format_path([]), "/")
        self.assertEqual(format_path(["a", "b"]), "/a/b")


class LsTest(unittest.TestCase):
    """Проверка команды ls."""

    def setUp(self):
        """Создать оболочку с тестовой VFS."""
        self.shell = make_shell()

    def test_current_directory(self):
        """Без аргументов - текущая директория, скрытые не видны."""
        self.assertEqual(self.shell.execute("ls"), "a.txt  home")

    def test_all(self):
        """-a показывает скрытые файлы."""
        self.assertEqual(self.shell.execute("ls -a"), ".hidden  a.txt  home")

    def test_long(self):
        """-l выводит тип, размер и имя."""
        self.assertEqual(
            self.shell.execute("ls -l"),
            "-        8 a.txt\nd        - home",
        )

    def test_combined_options(self):
        """-al - объединенные опции."""
        self.assertIn(".hidden", self.shell.execute("ls -al"))

    def test_file_and_directories(self):
        """Файлы выводятся по имени, директории - с заголовками."""
        output = self.shell.execute("ls /a.txt home home/empty")
        self.assertEqual(
            output, "/a.txt\n\nhome:\nempty  user\n\nhome/empty:"
        )

    def test_missing_path(self):
        """Отсутствующий путь - ошибка, остальные выводятся."""
        with self.assertRaises(CommandError) as context:
            self.shell.execute("ls nope home")
        self.assertIn("cannot access 'nope'", str(context.exception))
        self.assertEqual(context.exception.output, "home:\nempty  user")

    def test_invalid_option(self):
        """Неизвестная опция - ошибка."""
        with self.assertRaisesRegex(CommandError, "invalid option"):
            self.shell.execute("ls -z")


class CdTest(unittest.TestCase):
    """Проверка команды cd."""

    def setUp(self):
        """Создать оболочку с тестовой VFS."""
        self.shell = make_shell()

    def test_relative_and_parent(self):
        """Переход по относительному пути и на уровень выше."""
        self.shell.execute("cd home/user")
        self.assertEqual(self.shell.cwd, ["home", "user"])
        self.shell.execute("cd ..")
        self.assertEqual(self.shell.cwd, ["home"])

    def test_home(self):
        """cd без аргументов и cd ~ - в корень."""
        for line in ("cd", "cd ~"):
            self.shell.execute("cd /home/user")
            self.shell.execute(line)
            self.assertEqual(self.shell.cwd, [])

    def test_errors(self):
        """Нет пути, файл вместо директории, лишние аргументы."""
        cases = {
            "cd nope": "No such file or directory",
            "cd a.txt": "Not a directory",
            "cd a.txt/x": "Not a directory",
            "cd a b": "too many arguments",
        }
        for line, message in cases.items():
            with self.assertRaisesRegex(CommandError, message):
                self.shell.execute(line)
        self.assertEqual(self.shell.cwd, [])

    def test_ls_uses_cwd(self):
        """Относительные пути считаются от текущей директории."""
        self.shell.execute("cd /home")
        self.assertEqual(self.shell.execute("ls user"), "bin.dat  notes.txt")


class CatRevTest(unittest.TestCase):
    """Проверка команд cat и rev."""

    def setUp(self):
        """Создать оболочку с тестовой VFS."""
        self.shell = make_shell()

    def test_cat(self):
        """cat выводит содержимое без завершающего перевода строки."""
        self.assertEqual(self.shell.execute("cat a.txt"), "one\ntwo")

    def test_cat_several_files(self):
        """Несколько файлов объединяются, CRLF заменяется на LF."""
        output = self.shell.execute("cat a.txt home/user/notes.txt")
        self.assertEqual(output, "one\ntwo\nпривет")

    def test_cat_invalid_utf8(self):
        """Некорректные байты заменяются, а не вызывают сбой."""
        self.assertEqual(
            self.shell.execute("cat home/user/bin.dat"), "�"
        )

    def test_rev(self):
        """rev переворачивает каждую строку."""
        self.assertEqual(self.shell.execute("rev a.txt"), "eno\nowt")
        output = self.shell.execute("rev home/user/notes.txt")
        self.assertEqual(output, "тевирп")

    def test_errors_with_partial_output(self):
        """Ошибки по отдельным файлам, остальные выводятся."""
        for name in ("cat", "rev"):
            with self.assertRaises(CommandError) as context:
                self.shell.execute(f"{name} home nope a.txt")
            message = str(context.exception)
            self.assertIn(f"{name}: home: Is a directory", message)
            self.assertIn(f"{name}: nope: No such file", message)
            self.assertTrue(context.exception.output)

    def test_missing_operand(self):
        """Без файлов - ошибка."""
        for name in ("cat", "rev"):
            with self.assertRaisesRegex(CommandError, "missing file"):
                self.shell.execute(name)


class HistoryTest(unittest.TestCase):
    """Проверка команды history."""

    def setUp(self):
        """Создать оболочку и выполнить несколько команд."""
        self.shell = make_shell()
        for line in ("ls", "cd home", "foo"):
            try:
                self.shell.execute(line)
            except CommandError:
                pass

    def test_full_history(self):
        """Выводятся все команды с номерами, включая history."""
        self.assertEqual(
            self.shell.execute("history"),
            "    1  ls\n    2  cd home\n    3  foo\n    4  history",
        )

    def test_last_entries(self):
        """history N - последние N записей."""
        self.assertEqual(
            self.shell.execute("history 2"),
            "    3  foo\n    4  history 2",
        )
        self.assertEqual(self.shell.execute("history 0"), "")
        self.assertIn("    1  ls", self.shell.execute("history 99"))

    def test_errors(self):
        """Нечисловой, отрицательный и лишний аргумент - ошибки."""
        cases = {
            "history x": "numeric argument required",
            "history -1": "invalid option",
            "history 1 2": "too many arguments",
        }
        for line, message in cases.items():
            with self.assertRaisesRegex(CommandError, message):
                self.shell.execute(line)


if __name__ == "__main__":
    unittest.main()
