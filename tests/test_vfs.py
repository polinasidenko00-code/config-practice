"""Тесты загрузки и сохранения VFS."""

import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), os.pardir, "src")
)

from emulator.commands import CommandError  # noqa: E402
from emulator.config import create_vfs, parse_args  # noqa: E402
from emulator.shell import Shell  # noqa: E402
from emulator.vfs import (  # noqa: E402
    Vfs,
    VfsDir,
    VfsError,
    load_vfs,
    save_vfs,
)

TREE = {
    "readme.txt": b"top level\n",
    "home/user/docs/report.txt": b"report\n",
    "home/user/notes.txt": "заметки\n".encode("utf-8"),
    "bin/tool": bytes(range(256)),
}


def make_tree(root, tree):
    """Создать на диске файлы из словаря путь -> содержимое."""
    for relative, data in tree.items():
        path = os.path.join(root, *relative.split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as file:
            file.write(data)


def read_tree(root):
    """Прочитать все файлы директории в словарь путь -> содержимое."""
    tree = {}
    for current, _dirs, files in os.walk(root):
        for name in files:
            path = os.path.join(current, name)
            relative = os.path.relpath(path, root).replace(os.sep, "/")
            with open(path, "rb") as file:
                tree[relative] = file.read()
    return tree


class VfsTestCase(unittest.TestCase):
    """Базовый класс: временная директория с деревом файлов."""

    def setUp(self):
        """Создать временную директорию с исходной VFS."""
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.tmp = temp.name
        self.source = os.path.join(self.tmp, "source")
        make_tree(self.source, TREE)


class LoadVfsTest(VfsTestCase):
    """Проверка загрузки VFS в память."""

    def test_structure_loaded(self):
        """Директории и файлы всех уровней загружены в память."""
        vfs = load_vfs(self.source, "src")
        docs = vfs.root.children["home"].children["user"]
        report = docs.children["docs"].children["report.txt"]
        self.assertEqual(report.data, b"report\n")
        self.assertEqual(vfs.count(), (4, 4))
        self.assertEqual(vfs.name, "src")

    def test_binary_content(self):
        """Содержимое файлов хранится как байты без изменений."""
        vfs = load_vfs(self.source)
        tool = vfs.root.children["bin"].children["tool"]
        self.assertEqual(tool.data, bytes(range(256)))

    def test_source_not_modified(self):
        """Загрузка не изменяет исходную директорию."""
        load_vfs(self.source)
        self.assertEqual(read_tree(self.source), TREE)

    def test_missing_path(self):
        """Несуществующий путь - ошибка загрузки."""
        missing = os.path.join(self.tmp, "missing")
        with self.assertRaisesRegex(VfsError, "no such file"):
            load_vfs(missing)

    def test_file_instead_of_directory(self):
        """Файл вместо директории - неверный формат."""
        path = os.path.join(self.source, "readme.txt")
        with self.assertRaisesRegex(VfsError, "invalid format"):
            load_vfs(path)

    def test_unsupported_entry(self):
        """Ссылка или устройство внутри VFS - неверный формат."""
        entry = mock.Mock(path="vfs/link")
        entry.is_dir.return_value = False
        entry.is_file.return_value = False
        with mock.patch("os.scandir") as scandir:
            scandir.return_value.__enter__.return_value = [entry]
            with self.assertRaisesRegex(VfsError, "unsupported"):
                load_vfs(self.source)

    def test_empty_vfs_without_path(self):
        """Без параметра --vfs создается пустая VFS."""
        vfs = create_vfs(parse_args([]))
        self.assertEqual((vfs.name, vfs.count()), ("vfs", (0, 0)))


class SaveVfsTest(VfsTestCase):
    """Проверка сохранения VFS на диск."""

    def test_round_trip(self):
        """Сохраненная VFS совпадает с исходной директорией."""
        target = os.path.join(self.tmp, "copy")
        save_vfs(load_vfs(self.source), target)
        self.assertEqual(read_tree(target), TREE)

    def test_memory_changes_saved(self):
        """Сохраняется состояние VFS в памяти."""
        vfs = load_vfs(self.source)
        vfs.root.add(VfsDir("new_dir"))
        del vfs.root.children["bin"]
        target = os.path.join(self.tmp, "copy")
        save_vfs(vfs, target)
        self.assertTrue(os.path.isdir(os.path.join(target, "new_dir")))
        self.assertFalse(os.path.exists(os.path.join(target, "bin")))
        self.assertIn("bin/tool", read_tree(self.source))

    def test_existing_empty_directory(self):
        """Сохранение в существующую пустую директорию."""
        target = os.path.join(self.tmp, "empty")
        os.mkdir(target)
        save_vfs(load_vfs(self.source), target)
        self.assertEqual(read_tree(target), TREE)

    def test_non_empty_directory(self):
        """Непустая директория назначения - ошибка."""
        with self.assertRaisesRegex(VfsError, "not empty"):
            save_vfs(Vfs(), self.source)

    def test_file_as_target(self):
        """Файл в качестве назначения - ошибка."""
        target = os.path.join(self.source, "readme.txt")
        with self.assertRaisesRegex(VfsError, "not a directory"):
            save_vfs(Vfs(), target)


class VfsSaveCommandTest(VfsTestCase):
    """Проверка команды vfs-save."""

    def setUp(self):
        """Создать оболочку с загруженной VFS."""
        super().setUp()
        self.shell = Shell(load_vfs(self.source, "src"))

    def test_save(self):
        """vfs-save PATH сохраняет VFS и сообщает об этом."""
        target = os.path.join(self.tmp, "copy")
        output = self.shell.execute(f"vfs-save {target}")
        self.assertIn("saved to", output)
        self.assertEqual(read_tree(target), TREE)

    def test_wrong_arguments(self):
        """Без пути или с лишними аргументами - ошибка."""
        for line in ("vfs-save", "vfs-save a b"):
            with self.assertRaisesRegex(CommandError, "usage"):
                self.shell.execute(line)

    def test_save_error(self):
        """Ошибка сохранения сообщается как ошибка команды."""
        with self.assertRaisesRegex(CommandError, "not empty"):
            self.shell.execute(f"vfs-save {self.source}")


if __name__ == "__main__":
    unittest.main()
