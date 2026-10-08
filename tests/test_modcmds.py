"""Тесты команд этапа 5: chown и rm."""

import os
import tempfile
import unittest
from functools import cached_property

from emulator.commands import CommandError
from emulator.shell import Shell
from emulator.vfs import Vfs, VfsDir, VfsFile, load_vfs


def make_shell():
    """Создать оболочку с VFS: /a.txt, /d/b.txt, /d/sub/c.txt."""
    sub = VfsDir("sub")
    sub.add(VfsFile("c.txt", b"c"))
    directory = VfsDir("d")
    directory.add(VfsFile("b.txt", b"b"))
    directory.add(sub)
    vfs = Vfs("t")
    vfs.root.add(VfsFile("a.txt", b"a"))
    vfs.root.add(directory)
    return Shell(vfs)


def owner_of(shell, path):
    """Вернуть строку владелец:группа узла по пути."""
    node = shell.find(path)
    return f"{node.owner}:{node.group}"


class ChownTest(unittest.TestCase):
    """Проверка команды chown."""

    @cached_property
    def shell(self):
        """Оболочка с тестовой VFS, своя для каждого теста."""
        return make_shell()

    def test_default_owner(self):
        """По умолчанию владелец и группа - root."""
        self.assertEqual(owner_of(self.shell, "a.txt"), "root:root")

    def test_owner_and_group_forms(self):
        """OWNER, OWNER:GROUP, :GROUP и OWNER: меняют нужное."""
        cases = [
            ("alice", "alice:root"),
            ("bob:staff", "bob:staff"),
            (":dev", "bob:dev"),
            ("carol:", "carol:dev"),
        ]
        for spec, expected in cases:
            self.assertEqual(self.shell.execute(f"chown {spec} a.txt"), "")
            self.assertEqual(owner_of(self.shell, "a.txt"), expected)

    def test_not_recursive_by_default(self):
        """Без -R меняется только сама директория."""
        self.shell.execute("chown alice d")
        self.assertEqual(owner_of(self.shell, "d"), "alice:root")
        self.assertEqual(owner_of(self.shell, "d/b.txt"), "root:root")

    def test_recursive_verbose(self):
        """-R меняет все поддерево, -v сообщает о каждом узле."""
        output = self.shell.execute("chown -Rv alice:dev d")
        self.assertEqual(owner_of(self.shell, "d/sub/c.txt"), "alice:dev")
        self.assertEqual(len(output.splitlines()), 4)
        self.assertIn(
            "changed ownership of 'd/sub/c.txt' from root:root "
            "to alice:dev", output,
        )

    def test_retained(self):
        """-v сообщает, если владелец не изменился."""
        output = self.shell.execute("chown -v root a.txt")
        self.assertEqual(output, "ownership of 'a.txt' retained as root:root")

    def test_shown_in_ls(self):
        """ls -l показывает нового владельца."""
        self.shell.execute("chown alice:staff a.txt")
        self.assertIn("alice  staff", self.shell.execute("ls -l a.txt"))

    def test_errors(self):
        """Ошибки операндов, имен и опций."""
        cases = {
            "chown": "missing operand",
            "chown alice": "missing operand after 'alice'",
            "chown 1bad a.txt": "invalid user",
            "chown alice:-x a.txt": "invalid group",
            "chown : a.txt": "invalid spec",
            "chown -x alice a.txt": "invalid option",
        }
        for line, message in cases.items():
            with self.assertRaisesRegex(CommandError, message):
                self.shell.execute(line)
        self.assertEqual(owner_of(self.shell, "a.txt"), "root:root")

    def test_missing_path_with_others(self):
        """Ненайденный путь - ошибка, остальные пути обработаны."""
        with self.assertRaisesRegex(CommandError, "cannot access 'nope'"):
            self.shell.execute("chown alice nope a.txt")
        self.assertEqual(owner_of(self.shell, "a.txt"), "alice:root")


class RmTest(unittest.TestCase):
    """Проверка команды rm."""

    @cached_property
    def shell(self):
        """Оболочка с тестовой VFS, своя для каждого теста."""
        return make_shell()

    def test_remove_file(self):
        """rm удаляет файл из VFS."""
        self.assertEqual(self.shell.execute("rm a.txt"), "")
        self.assertEqual(self.shell.execute("ls"), "d")

    def test_directory_needs_recursive(self):
        """Директория без -r не удаляется."""
        with self.assertRaisesRegex(CommandError, "Is a directory"):
            self.shell.execute("rm d")
        self.assertIn("d", self.shell.execute("ls"))

    def test_recursive_verbose(self):
        """-rv удаляет поддерево, сообщая о детях до родителей."""
        output = self.shell.execute("rm -rv d")
        self.assertEqual(output.splitlines(), [
            "removed 'd/sub/c.txt'",
            "removed directory 'd/sub'",
            "removed 'd/b.txt'",
            "removed directory 'd'",
        ])
        self.assertEqual(self.shell.execute("ls"), "a.txt")

    def test_capital_r_and_relative_path(self):
        """-R равносилен -r; пути считаются от текущей директории."""
        self.shell.execute("cd d")
        self.shell.execute("rm -R sub ../a.txt")
        self.assertEqual(self.shell.execute("ls /"), "d")
        self.assertEqual(self.shell.execute("ls"), "b.txt")

    def test_force(self):
        """-f скрывает отсутствующие пути и отсутствие операндов."""
        self.assertEqual(self.shell.execute("rm -f"), "")
        self.assertEqual(self.shell.execute("rm -f nope a.txt"), "")
        self.assertEqual(self.shell.execute("ls"), "d")

    def test_force_keeps_other_errors(self):
        """-f не скрывает ошибку удаления директории."""
        with self.assertRaisesRegex(CommandError, "Is a directory"):
            self.shell.execute("rm -f d")

    def test_errors(self):
        """Ошибки: нет операнда, нет пути, ., .., корень, опция."""
        cases = {
            "rm": "missing operand",
            "rm nope": "cannot remove 'nope': No such file",
            "rm a.txt/x": "Not a directory",
            "rm .": "refusing to remove",
            "rm -r d/..": "refusing to remove",
            "rm /": "Is a directory",
            "rm -r /": "dangerous to operate recursively",
            "rm -z a.txt": "invalid option",
        }
        for line, message in cases.items():
            with self.assertRaisesRegex(CommandError, message):
                self.shell.execute(line)
        self.assertEqual(self.shell.execute("ls"), "a.txt  d")

    def test_missing_path_with_others(self):
        """Ненайденный путь - ошибка, остальные пути удалены."""
        with self.assertRaises(CommandError):
            self.shell.execute("rm nope a.txt")
        self.assertEqual(self.shell.execute("ls"), "d")


class InMemoryTest(unittest.TestCase):
    """Изменения VFS не затрагивают исходную директорию."""

    def test_source_unchanged(self):
        """chown и rm меняют только память."""
        with tempfile.TemporaryDirectory() as tmp:
            os.makedirs(os.path.join(tmp, "src", "d"))
            path = os.path.join(tmp, "src", "d", "f.txt")
            with open(path, "wb") as file:
                file.write(b"data")
            shell = Shell(load_vfs(os.path.join(tmp, "src")))
            shell.execute("chown -R alice /")
            shell.execute("rm -r d")
            self.assertEqual(shell.execute("ls"), "")
            self.assertTrue(os.path.isfile(path))


if __name__ == "__main__":
    unittest.main()
