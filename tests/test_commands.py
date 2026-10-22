"""Тесты команд этапа 4: пути в VFS, ls, cd, tail, tac."""

import os
import unittest

from shell import Message, Shell
from vfs import VfsPathError, load_vfs, resolve

DEEP_VFS = os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.pardir, "examples", "vfs", "deep.xml"))
TODO = "/home/guest/docs/todo.txt"
TODO_LINES = 12
DEFAULT_TAIL = 10


def texts(messages):
    """Тексты сообщений списком."""
    return [message.text for message in messages]


class CommandTestCase(unittest.TestCase):
    """Базовый класс: оболочка с VFS examples/vfs/deep.xml.

    Структура: /home/user/{notes.txt, logo.png}, /home/guest/docs/
    {todo.txt, drafts/old/letter.txt}, /readme.txt.
    """

    def setUp(self):
        """Загружает VFS и создаёт оболочку в корне."""
        self.vfs = load_vfs(DEEP_VFS, "deep")
        self.shell = Shell(self.vfs)

    def run_ok(self, line):
        """Выполняет команду без ошибки и возвращает тексты вывода."""
        result = self.shell.execute(line)
        self.assertFalse(any(m.is_error for m in result), result)
        return texts(result)

    def assert_error(self, line, text):
        """Проверяет, что команда выдаёт ровно одну ошибку с текстом text."""
        self.assertEqual(self.shell.execute(line), [Message(text, True)])


class ResolveTests(CommandTestCase):
    """Проверки поиска узла по пути."""

    def path_of(self, cwd, path):
        """Абсолютный путь, который получится из path в каталоге cwd."""
        return resolve(self.vfs, cwd, path)[1]

    def test_absolute_and_relative(self):
        """Абсолютный путь не зависит от cwd, относительный — зависит."""
        self.assertEqual(self.path_of("/home", "/readme.txt"), "/readme.txt")
        self.assertEqual(self.path_of("/home", "user"), "/home/user")

    def test_dot_and_dotdot(self):
        """'.' — текущий каталог, '..' — родитель."""
        self.assertEqual(self.path_of("/home/user", "."), "/home/user")
        self.assertEqual(self.path_of("/home/user", "../guest/./docs"),
                         "/home/guest/docs")

    def test_cannot_go_above_root(self):
        """Выше корня подняться нельзя."""
        self.assertEqual(self.path_of("/home", "../../.."), "/")

    def test_extra_slashes(self):
        """Повторные и завершающие слэши не мешают."""
        self.assertEqual(self.path_of("/", "//home///user/"), "/home/user")

    def test_not_found(self):
        """Несуществующий путь — ошибка."""
        with self.assertRaises(VfsPathError):
            resolve(self.vfs, "/", "/home/nobody")

    def test_through_file(self):
        """Путь через файл — ошибка «не каталог»."""
        with self.assertRaises(VfsPathError) as context:
            resolve(self.vfs, "/", "readme.txt/x")
        self.assertEqual(str(context.exception), "не каталог")

    def test_empty_path(self):
        """Пустой путь — ошибка."""
        with self.assertRaises(VfsPathError):
            resolve(self.vfs, "/", "")


class LsTests(CommandTestCase):
    """Проверки ls."""

    def test_current_dir_sorted_with_slash(self):
        """Содержимое по алфавиту, каталоги с '/' на конце."""
        self.assertEqual(self.run_ok("ls"), ["home/", "readme.txt"])

    def test_absolute_and_relative_path(self):
        """ls с абсолютным и относительным путём."""
        self.assertEqual(self.run_ok("ls /home"), ["guest/", "user/"])
        self.assertEqual(self.run_ok("ls home/user"),
                         ["logo.png", "notes.txt"])

    def test_file_prints_its_name(self):
        """ls для файла выводит его имя."""
        self.assertEqual(self.run_ok("ls /home/user/notes.txt"),
                         ["notes.txt"])

    def test_nested_dirs(self):
        """ls во вложенных каталогах, путь относительно текущего."""
        self.run_ok("cd /home/guest/docs/drafts")
        self.assertEqual(self.run_ok("ls"), ["old/"])
        self.assertEqual(self.run_ok("ls old"), ["letter.txt"])

    def test_errors(self):
        """Ошибки ls: нет пути, лишние аргументы, ключ."""
        self.assert_error("ls nope", "ls: nope: нет такого файла или каталога")
        self.assert_error("ls / /home", "ls: слишком много аргументов")
        self.assert_error("ls -l", "ls: неизвестный ключ -l")


class CdTests(CommandTestCase):
    """Проверки cd и приглашения."""

    def test_cd_changes_prompt(self):
        """После cd приглашение показывает новый каталог."""
        self.assertEqual(self.run_ok("cd home/user"), [])
        self.assertEqual(self.shell.cwd, "/home/user")
        self.assertTrue(self.shell.prompt.endswith(":/home/user$ "))

    def test_dotdot_and_root(self):
        """cd .. поднимается, выше корня — остаётся в корне."""
        self.run_ok("cd /home/user")
        self.run_ok("cd ../..")
        self.assertEqual(self.shell.cwd, "/")
        self.run_ok("cd ..")
        self.assertEqual(self.shell.cwd, "/")

    def test_no_args_goes_to_root(self):
        """cd без аргумента переходит в корень."""
        self.run_ok("cd /home/guest/docs")
        self.run_ok("cd")
        self.assertEqual(self.shell.cwd, "/")

    def test_relative_after_cd(self):
        """Относительные пути считаются от текущего каталога."""
        self.run_ok("cd /home")
        self.assertEqual(self.run_ok("ls user"), ["logo.png", "notes.txt"])

    def test_errors_do_not_change_cwd(self):
        """Ошибки cd не меняют текущий каталог."""
        self.run_ok("cd /home")
        self.assert_error("cd /readme.txt", "cd: /readme.txt: не каталог")
        self.assert_error("cd nobody",
                          "cd: nobody: нет такого файла или каталога")
        self.assert_error("cd a b", "cd: слишком много аргументов")
        self.assertEqual(self.shell.cwd, "/home")


class TacTests(CommandTestCase):
    """Проверки tac."""

    def test_reverse_lines(self):
        """Строки файла в обратном порядке."""
        self.assertEqual(self.run_ok("tac /home/user/notes.txt"),
                         ["вторая строка", "первая строка"])

    def test_relative_path(self):
        """Относительный путь от текущего каталога."""
        self.run_ok("cd /home/user")
        self.assertEqual(self.run_ok("tac notes.txt")[0], "вторая строка")

    def test_errors(self):
        """Ошибки tac: каталог, двоичный файл, нет файла, число аргументов."""
        self.assert_error("tac home", "tac: home: это каталог")
        self.assert_error("tac /home/user/logo.png",
                          "tac: /home/user/logo.png: двоичный файл")
        self.assert_error("tac nope",
                          "tac: nope: нет такого файла или каталога")
        self.assert_error("tac", "tac: требуется один аргумент — файл")
        self.assert_error("tac a b", "tac: требуется один аргумент — файл")


class TailTests(CommandTestCase):
    """Проверки tail."""

    def test_default_ten_lines(self):
        """По умолчанию — последние 10 строк."""
        lines = self.run_ok(f"tail {TODO}")
        self.assertEqual(len(lines), DEFAULT_TAIL)
        self.assertEqual(lines[-1], f"{TODO_LINES}. начать этап 5")

    def test_n_option(self):
        """tail -n N — последние N строк."""
        self.assertEqual(self.run_ok("tail -n 1 /home/user/notes.txt"),
                         ["вторая строка"])

    def test_n_zero_and_too_big(self):
        """-n 0 — пусто, N больше числа строк — весь файл."""
        self.assertEqual(self.run_ok("tail -n 0 /readme.txt"), [])
        self.assertEqual(len(self.run_ok(f"tail -n 100 {TODO}")),
                         TODO_LINES)

    def test_errors(self):
        """Ошибки tail: неверное N, нет файла, каталог, двоичный файл."""
        self.assert_error("tail -n abc /readme.txt",
                          "tail: -n abc: требуется неотрицательное число")
        self.assert_error("tail -n -1 /readme.txt",
                          "tail: -n -1: требуется неотрицательное число")
        self.assert_error("tail -n", "tail: -n: требуется неотрицательное "
                          "число")
        self.assert_error("tail -n 3", "tail: требуется один аргумент — файл")
        self.assert_error("tail /home", "tail: /home: это каталог")
        self.assert_error("tail /home/user/logo.png",
                          "tail: /home/user/logo.png: двоичный файл")


if __name__ == "__main__":
    unittest.main()
