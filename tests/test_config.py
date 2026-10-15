"""Тесты параметров командной строки и их отладочного вывода."""

import contextlib
import io
import unittest

from config import NOT_SET, Config, debug_lines, parse_args


class ParseArgsTests(unittest.TestCase):
    """Проверки функции parse_args."""

    def test_no_params(self):
        """Без параметров оба пути не заданы."""
        self.assertEqual(parse_args([]), Config(None, None))

    def test_only_vfs(self):
        """Параметр --vfs задаёт путь к VFS."""
        config = parse_args(["--vfs", "disk.xml"])
        self.assertEqual(config, Config("disk.xml", None))

    def test_only_script(self):
        """Параметр --script задаёт путь к стартовому скрипту."""
        config = parse_args(["--script", "start.emu"])
        self.assertEqual(config, Config(None, "start.emu"))

    def test_both_params(self):
        """Оба параметра можно задать вместе."""
        config = parse_args(["--vfs", "disk.xml", "--script", "s.emu"])
        self.assertEqual(config, Config("disk.xml", "s.emu"))

    def test_order_does_not_matter(self):
        """Порядок параметров не важен."""
        config = parse_args(["--script", "s.emu", "--vfs", "disk.xml"])
        self.assertEqual(config, Config("disk.xml", "s.emu"))

    def test_equals_form(self):
        """Допустима форма --имя=значение."""
        config = parse_args(["--vfs=disk.xml", "--script=s.emu"])
        self.assertEqual(config, Config("disk.xml", "s.emu"))

    def test_path_with_spaces(self):
        """Путь с пробелами передаётся одним аргументом."""
        config = parse_args(["--vfs", "my dir/disk.xml"])
        self.assertEqual(config.vfs_path, "my dir/disk.xml")

    def _assert_exits_with_error(self, argv):
        """Проверяет, что разбор argv завершает программу с кодом 2."""
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as context:
                parse_args(argv)
        self.assertEqual(context.exception.code, 2)

    def test_unknown_option(self):
        """Неизвестный параметр — ошибка."""
        self._assert_exits_with_error(["--bogus"])

    def test_missing_value(self):
        """Параметр без значения — ошибка."""
        self._assert_exits_with_error(["--vfs"])

    def test_abbreviation_not_allowed(self):
        """Сокращения параметров не поддерживаются."""
        self._assert_exits_with_error(["--vf", "disk.xml"])

    def test_positional_not_allowed(self):
        """Позиционные аргументы не поддерживаются."""
        self._assert_exits_with_error(["disk.xml"])


class VfsNameTests(unittest.TestCase):
    """Проверки имени VFS для заголовка окна."""

    def test_default_name(self):
        """Без --vfs используется имя по умолчанию."""
        self.assertEqual(Config().vfs_name, "vfs")

    def test_name_without_extension(self):
        """Имя — это имя файла без расширения и каталогов."""
        self.assertEqual(Config("data/disk.xml").vfs_name, "disk")

    def test_directory_with_trailing_slash(self):
        """Завершающий слэш не даёт пустого имени."""
        self.assertEqual(Config("data/myfs/").vfs_name, "myfs")

    def test_empty_path(self):
        """Пустой путь даёт имя по умолчанию."""
        self.assertEqual(Config("").vfs_name, "vfs")


class DebugLinesTests(unittest.TestCase):
    """Проверки отладочного вывода параметров."""

    def test_shows_all_params(self):
        """В выводе есть оба пути и имя VFS."""
        text = "\n".join(debug_lines(Config("data/disk.xml", "s.emu")))
        self.assertIn("data/disk.xml", text)
        self.assertIn("s.emu", text)
        self.assertIn("disk", text)

    def test_unset_params_are_marked(self):
        """Незаданные параметры помечаются явно."""
        lines = debug_lines(Config())
        self.assertEqual(sum(NOT_SET in line for line in lines), 2)

    def test_lines_have_debug_prefix(self):
        """Каждая строка начинается с метки [debug]."""
        for line in debug_lines(Config("a.xml", "b.emu")):
            self.assertTrue(line.startswith("[debug]"))


if __name__ == "__main__":
    unittest.main()
