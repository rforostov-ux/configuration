"""Тесты оболочки: команды ls, cd, exit и обработка ошибок."""

import os
import unittest
from unittest import mock

from shell import Message, Shell, has_error
from vfs import empty_vfs

TEST_ENV = {"HOME": "/home/user", "USER": "user"}


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
class ShellTests(unittest.TestCase):
    """Проверки метода Shell.execute."""

    def setUp(self):
        """Создаёт новую оболочку перед каждым тестом."""
        self.shell = Shell(empty_vfs("test_vfs"))

    def test_vfs_name(self):
        """Имя VFS сохраняется в оболочке."""
        self.assertEqual(self.shell.vfs_name, "test_vfs")

    def test_ls_without_args(self):
        """ls без аргументов сообщает, что аргументов нет."""
        self.assertEqual(self.shell.execute("ls"),
                         [Message("ls: заглушка, аргументов нет")])

    def test_ls_with_args_and_env(self):
        """ls печатает аргументы после раскрытия переменных."""
        self.assertEqual(self.shell.execute("ls -l $HOME"), [
            Message("ls: заглушка, аргументов: 2"),
            Message('  1) "-l"'),
            Message('  2) "/home/user"'),
        ])

    def test_ls_space_and_empty_args(self):
        """Аргумент с пробелом и пустой аргумент видны в кавычках."""
        self.assertEqual(self.shell.execute('ls "my dir" ""'), [
            Message("ls: заглушка, аргументов: 2"),
            Message('  1) "my dir"'),
            Message('  2) ""'),
        ])

    def test_cd_with_arg(self):
        """cd печатает свой аргумент."""
        self.assertEqual(self.shell.execute("cd /tmp"), [
            Message("cd: заглушка, аргументов: 1"),
            Message('  1) "/tmp"'),
        ])

    def test_cd_too_many_args(self):
        """cd с двумя аргументами — ошибка."""
        self.assertEqual(self.shell.execute("cd a b"),
                         [Message("cd: слишком много аргументов", True)])

    def test_unknown_command(self):
        """Неизвестная команда — ошибка."""
        self.assertEqual(self.shell.execute("foo"),
                         [Message("foo: команда не найдена", True)])

    def test_syntax_error(self):
        """Незакрытая кавычка — синтаксическая ошибка."""
        result = self.shell.execute('ls "abc')
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].is_error)

    def test_empty_line(self):
        """Пустая строка ничего не выводит."""
        self.assertEqual(self.shell.execute(""), [])

    def test_exit_default_code(self):
        """exit без аргументов завершает с кодом 0."""
        self.shell.execute("exit")
        self.assertEqual(self.shell.exit_code, 0)

    def test_exit_with_code(self):
        """exit 3 завершает с кодом 3."""
        self.shell.execute("exit 3")
        self.assertEqual(self.shell.exit_code, 3)

    def test_exit_not_a_number(self):
        """exit abc — ошибка, оболочка продолжает работать."""
        result = self.shell.execute("exit abc")
        self.assertTrue(result[0].is_error)
        self.assertIsNone(self.shell.exit_code)

    def test_exit_too_many_args(self):
        """exit 1 2 — ошибка, оболочка продолжает работать."""
        result = self.shell.execute("exit 1 2")
        self.assertTrue(result[0].is_error)
        self.assertIsNone(self.shell.exit_code)

    def test_has_error_true(self):
        """has_error находит ошибку среди сообщений."""
        messages = [Message("ok"), Message("bad", True)]
        self.assertTrue(has_error(messages))

    def test_has_error_false(self):
        """has_error ложно, если все сообщения обычные."""
        self.assertFalse(has_error([Message("ok")]))
        self.assertFalse(has_error([]))


if __name__ == "__main__":
    unittest.main()
