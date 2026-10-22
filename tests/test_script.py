"""Тесты стартового скрипта и сборки стартовых сообщений."""

import os
import tempfile
import unittest
from unittest import mock

from config import Config
from script import ScriptError, read_script, run_script
from shell import Message, Shell
from startup import build_startup
from vfs import Vfs, VfsDir, VfsFile

TEST_ENV = {"HOME": "/home/user"}


def small_vfs():
    """VFS для тестов: каталог /tmp с одним файлом a.txt."""
    tmp = VfsDir("tmp", {"a.txt": VfsFile("a.txt", b"x")})
    return Vfs("test_vfs", VfsDir("", {"tmp": tmp}))


def texts(messages):
    """Возвращает тексты сообщений списком."""
    return [message.text for message in messages]


class ScriptTestCase(unittest.TestCase):
    """Базовый класс: временная папка и оболочка для каждого теста."""

    def setUp(self):
        """Создаёт временную папку и оболочку."""
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.shell = Shell(small_vfs())

    def write_script(self, content, encoding="utf-8"):
        """Записывает скрипт во временную папку и возвращает путь."""
        path = os.path.join(self.tmp.name, "start.emu")
        with open(path, "w", encoding=encoding, newline="") as file:
            file.write(content)
        return path


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
class RunScriptTests(ScriptTestCase):
    """Проверки run_script: диалог, остановка на ошибке, exit."""

    def test_shows_input_and_output(self):
        """В диалоге есть и введённая команда, и её вывод."""
        path = self.write_script("ls $NOPE/tmp\n")
        result = run_script(self.shell, path)
        self.assertEqual(result, [
            Message(self.shell.prompt + "ls $NOPE/tmp"),
            Message("a.txt"),
        ])

    def test_blank_lines_are_skipped(self):
        """Пустые строки не попадают в диалог."""
        path = self.write_script("\nls\n   \ncd /tmp\n")
        result = run_script(self.shell, path)
        self.assertEqual(len(result), 3)

    def test_comment_is_shown_without_output(self):
        """Комментарий показывается как ввод, но вывода не даёт."""
        path = self.write_script("# заметка\nls\n")
        result = run_script(self.shell, path)
        self.assertEqual(result[0], Message(self.shell.prompt + "# заметка"))
        self.assertEqual(len(result), 3)

    def test_stops_at_first_error(self):
        """После первой ошибки остальные строки не выполняются."""
        path = self.write_script("ls\nfoo\nls second\n")
        result = run_script(self.shell, path)
        self.assertNotIn("second", " ".join(texts(result)))
        self.assertTrue(result[-1].is_error)

    def test_error_report_has_line_number_and_path(self):
        """Сообщение об остановке содержит путь и номер строки."""
        path = self.write_script("ls\n\nfoo\n")
        result = run_script(self.shell, path)
        self.assertIn(path, result[-1].text)
        self.assertIn("строка 3", result[-1].text)

    def test_command_error_is_in_transcript(self):
        """Сама ошибка команды тоже видна в диалоге."""
        path = self.write_script("foo\n")
        result = run_script(self.shell, path)
        self.assertEqual(result[1], Message("foo: команда не найдена", True))

    def test_syntax_error_stops_script(self):
        """Синтаксическая ошибка тоже останавливает скрипт."""
        path = self.write_script('ls "abc\nls after\n')
        result = run_script(self.shell, path)
        self.assertNotIn("after", " ".join(texts(result)))
        self.assertIn("строка 1", result[-1].text)

    def test_cd_error_stops_script(self):
        """Ошибка в аргументах команды останавливает скрипт."""
        path = self.write_script("cd a b\nls after\n")
        result = run_script(self.shell, path)
        self.assertNotIn("after", " ".join(texts(result)))

    def test_exit_stops_script_and_sets_code(self):
        """exit завершает скрипт и сохраняет код выхода."""
        path = self.write_script("ls\nexit 3\nls after\n")
        result = run_script(self.shell, path)
        self.assertEqual(self.shell.exit_code, 3)
        self.assertNotIn("after", " ".join(texts(result)))

    def test_exit_error_does_not_stop_with_code(self):
        """Неверный exit — ошибка скрипта, кода выхода нет."""
        path = self.write_script("exit abc\n")
        result = run_script(self.shell, path)
        self.assertTrue(result[-1].is_error)
        self.assertIsNone(self.shell.exit_code)

    def test_empty_script(self):
        """Пустой скрипт ничего не выводит."""
        path = self.write_script("")
        self.assertEqual(run_script(self.shell, path), [])

    def test_crlf_line_endings(self):
        """Строки с переводом CRLF (Windows) читаются правильно."""
        path = self.write_script("ls\r\ncd /tmp\r\n")
        result = run_script(self.shell, path)
        self.assertEqual(texts(result)[1], "tmp/")
        self.assertEqual(self.shell.cwd, "/tmp")

    def test_utf8_bom(self):
        """Метка BOM в начале файла (Блокнот Windows) не мешает."""
        path = self.write_script("ls\n", encoding="utf-8-sig")
        result = run_script(self.shell, path)
        self.assertEqual(result[0], Message(self.shell.prompt + "ls"))


class ReadScriptErrorTests(ScriptTestCase):
    """Проверки ошибок чтения файла скрипта."""

    def test_missing_file(self):
        """Нет файла — ScriptError."""
        with self.assertRaises(ScriptError):
            read_script(os.path.join(self.tmp.name, "nope.emu"))

    def test_directory_instead_of_file(self):
        """Каталог вместо файла — ScriptError."""
        with self.assertRaises(ScriptError):
            read_script(self.tmp.name)

    def test_wrong_encoding(self):
        """Файл не в UTF-8 — ScriptError."""
        path = os.path.join(self.tmp.name, "bad.emu")
        with open(path, "wb") as file:
            file.write(b"ls \xff\xfe\n")
        with self.assertRaises(ScriptError):
            read_script(path)

    def test_missing_file_reported_as_message(self):
        """run_script превращает ошибку чтения в сообщение."""
        result = run_script(self.shell, "no/such/file.emu")
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].is_error)
        self.assertIn("файл не найден", result[0].text)


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
class BuildStartupTests(ScriptTestCase):
    """Проверки build_startup: отладочный вывод и запуск скрипта."""

    def test_debug_output_without_script(self):
        """Без скрипта показывается только отладочный вывод."""
        result = build_startup(Config("disk.xml", None), self.shell)
        self.assertTrue(all(m.text.startswith("[debug]") for m in result))
        self.assertIn("disk.xml", " ".join(texts(result)))

    def test_debug_output_comes_before_script(self):
        """Отладочный вывод идёт раньше диалога скрипта."""
        path = self.write_script("ls\n")
        result = build_startup(Config(None, path), self.shell)
        self.assertTrue(result[0].text.startswith("[debug]"))
        self.assertEqual(result[-1], Message("tmp/"))

    def test_script_error_reaches_startup(self):
        """Ошибка скрипта попадает в стартовые сообщения."""
        path = self.write_script("foo\n")
        result = build_startup(Config(None, path), self.shell)
        self.assertTrue(result[-1].is_error)


if __name__ == "__main__":
    unittest.main()
