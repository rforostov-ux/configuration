"""Тесты VFS: загрузка из XML, ошибки, vfs-info и запуск с --vfs."""

import os
import tempfile
import unittest

from config import Config
from shell import Message, Shell
from startup import build_startup, open_vfs
from vfs import VfsDir, VfsError, VfsFile, empty_vfs, load_vfs

EXAMPLES = os.path.join(os.path.dirname(__file__), os.pardir, "examples")
VFS_EXAMPLES = os.path.abspath(os.path.join(EXAMPLES, "vfs"))
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def example(name):
    """Путь к примеру VFS из examples/vfs."""
    return os.path.join(VFS_EXAMPLES, name)


def depth(directory):
    """Глубина дерева каталогов: число уровней вложенности."""
    levels = [depth(node) for node in directory.children.values()
              if isinstance(node, VfsDir)]
    return 1 + max(levels, default=0)


class VfsTestCase(unittest.TestCase):
    """Базовый класс: временная папка для XML-файлов."""

    def setUp(self):
        """Создаёт временную папку."""
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def write_xml(self, content):
        """Записывает XML во временный файл и возвращает путь."""
        path = os.path.join(self.tmp.name, "disk.xml")
        with open(path, "w", encoding="utf-8") as file:
            file.write(content)
        return path

    def load(self, content):
        """Загружает VFS из строки XML."""
        return load_vfs(self.write_xml(content), "disk")

    def assert_load_error(self, content, text):
        """Проверяет, что загрузка падает с ошибкой, содержащей text."""
        with self.assertRaises(VfsError) as context:
            self.load(content)
        self.assertIn(text, str(context.exception))


class LoadVfsTests(VfsTestCase):
    """Проверки загрузки корректной VFS."""

    def test_structure(self):
        """Каталоги и файлы попадают в дерево с правильными именами."""
        vfs = self.load('<vfs><dir name="home"><file name="a.txt">hi'
                        '</file></dir><file name="b.txt"/></vfs>')
        home = vfs.root.children["home"]
        self.assertIsInstance(home, VfsDir)
        self.assertEqual(home.children["a.txt"], VfsFile("a.txt", b"hi"))
        self.assertEqual(vfs.root.children["b.txt"].data, b"")

    def test_text_is_utf8_bytes(self):
        """Текст файла хранится в байтах UTF-8 вместе с переводами строк."""
        vfs = self.load('<vfs><file name="n.txt">строка 1\nстрока 2'
                        '</file></vfs>')
        data = vfs.root.children["n.txt"].data
        self.assertEqual(data.decode("utf-8"), "строка 1\nстрока 2")

    def test_base64_is_decoded(self):
        """Двоичные данные из base64 декодируются при загрузке."""
        vfs = self.load('<vfs><file name="l.png" encoding="base64">\n'
                        '  iVBORw0K\n  Ggo=\n</file></vfs>')
        node = vfs.root.children["l.png"]
        self.assertEqual(node.data, PNG_SIGNATURE)
        self.assertTrue(node.binary)

    def test_name_and_source(self):
        """VFS хранит имя и путь к источнику."""
        path = self.write_xml("<vfs/>")
        vfs = load_vfs(path, "disk")
        self.assertEqual((vfs.name, vfs.source), ("disk", path))

    def test_count(self):
        """count считает каталоги (без корня) и файлы на всех уровнях."""
        vfs = self.load('<vfs><dir name="a"><dir name="b"><file name="f"/>'
                        '</dir></dir><file name="g"/></vfs>')
        self.assertEqual(vfs.count(), (2, 2))

    def test_comments_are_ignored(self):
        """XML-комментарии не становятся файлами."""
        vfs = self.load("<vfs><!-- заметка --></vfs>")
        self.assertEqual(vfs.count(), (0, 0))

    def test_file_is_not_changed(self):
        """Загрузка не меняет XML-файл на диске."""
        path = self.write_xml('<vfs><file name="a">x</file></vfs>')
        with open(path, "rb") as file:
            before = file.read()
        load_vfs(path, "disk")
        with open(path, "rb") as file:
            self.assertEqual(file.read(), before)


class LoadVfsErrorTests(VfsTestCase):
    """Проверки ошибок загрузки VFS."""

    def test_missing_file(self):
        """Нет файла — «файл не найден» с путём."""
        with self.assertRaises(VfsError) as context:
            load_vfs(os.path.join(self.tmp.name, "nope.xml"), "nope")
        self.assertIn("nope.xml: файл не найден", str(context.exception))

    def test_directory_instead_of_file(self):
        """Каталог вместо файла — ошибка загрузки."""
        with self.assertRaises(VfsError):
            load_vfs(self.tmp.name, "tmp")

    def test_broken_xml_reports_line(self):
        """Неверный XML — сообщение с номером строки."""
        self.assert_load_error("<vfs>\n<dir name='a'>\n</vfs>",
                               "неверный формат XML (строка 3)")

    def test_not_xml(self):
        """Обычный текст вместо XML — неверный формат."""
        self.assert_load_error("просто текст", "неверный формат XML")

    def test_wrong_root(self):
        """Корень не <vfs> — неизвестный элемент."""
        self.assert_load_error("<root/>", "неизвестный элемент <root>")

    def test_unknown_tag(self):
        """Неизвестный тег внутри — ошибка."""
        self.assert_load_error('<vfs><folder name="a"/></vfs>',
                               "неизвестный элемент <folder>")

    def test_missing_name(self):
        """Нет атрибута name — ошибка с указанием каталога."""
        self.assert_load_error('<vfs><dir name="home"><file/></dir></vfs>',
                               "каталог /home: элемент <file> без атрибута")

    def test_bad_names(self):
        """Пустое имя, имя со слэшем и имена . и .. запрещены."""
        for name in ("", "a/b", ".", ".."):
            with self.subTest(name=name):
                self.assert_load_error(f'<vfs><file name="{name}"/></vfs>',
                                       "недопустимое имя")

    def test_duplicate_name(self):
        """Повтор имени в одном каталоге — ошибка."""
        self.assert_load_error('<vfs><dir name="home"><dir name="user"/>'
                               '<file name="user"/></dir></vfs>',
                               "каталог /home: повторяется имя user")

    def test_same_name_in_other_dirs_is_ok(self):
        """Одинаковые имена в разных каталогах допустимы."""
        vfs = self.load('<vfs><dir name="a"><file name="x"/></dir>'
                        '<dir name="b"><file name="x"/></dir></vfs>')
        self.assertEqual(vfs.count(), (2, 2))

    def test_bad_base64(self):
        """Неверные данные base64 — ошибка с путём файла."""
        self.assert_load_error('<vfs><dir name="d"><file name="l.png" '
                               'encoding="base64">!!!</file></dir></vfs>',
                               "файл /d/l.png: неверные данные base64")

    def test_unknown_encoding(self):
        """Кодировка, отличная от base64, — ошибка."""
        self.assert_load_error('<vfs><file name="a" encoding="hex">00'
                               '</file></vfs>', "неизвестная кодировка hex")

    def test_element_inside_file(self):
        """Внутри <file> не может быть других элементов."""
        self.assert_load_error('<vfs><file name="a"><dir name="b"/></file>'
                               '</vfs>', "файл /a: внутри файла")


class ExampleVfsTests(unittest.TestCase):
    """Проверки примеров из examples/vfs."""

    def test_minimal(self):
        """minimal.xml — только корень."""
        vfs = load_vfs(example("minimal.xml"), "minimal")
        self.assertEqual(vfs.count(), (0, 0))

    def test_files(self):
        """files.xml — несколько файлов в корне, один двоичный."""
        vfs = load_vfs(example("files.xml"), "files")
        nodes = vfs.root.children.values()
        self.assertGreater(len(nodes), 1)
        self.assertTrue(all(isinstance(n, VfsFile) for n in nodes))
        self.assertTrue(any(n.binary for n in nodes))

    def test_deep(self):
        """deep.xml — не менее 3 уровней, 6 каталогов и 5 файлов."""
        vfs = load_vfs(example("deep.xml"), "deep")
        self.assertGreaterEqual(depth(vfs.root), 4)
        self.assertEqual(vfs.count(), (6, 5))

    def test_broken(self):
        """broken.xml — ошибка формата."""
        with self.assertRaises(VfsError) as context:
            load_vfs(example("broken.xml"), "broken")
        self.assertIn("неверный формат XML", str(context.exception))


class VfsInfoTests(unittest.TestCase):
    """Проверки служебной команды vfs-info."""

    def test_info_for_loaded_vfs(self):
        """vfs-info показывает имя, источник и число узлов."""
        shell = Shell(load_vfs(example("deep.xml"), "deep"))
        self.assertEqual(shell.execute("vfs-info"), [
            Message("VFS: deep"),
            Message(f"источник: {example('deep.xml')}"),
            Message("каталогов: 6, файлов: 5"),
        ])

    def test_info_for_empty_vfs(self):
        """Без --vfs источник не задан, узлов нет."""
        result = Shell(empty_vfs("vfs")).execute("vfs-info")
        self.assertEqual(result[1], Message("источник: <не задан>"))
        self.assertEqual(result[2], Message("каталогов: 0, файлов: 0"))

    def test_info_with_args_is_error(self):
        """vfs-info с аргументом — ошибка."""
        result = Shell(empty_vfs("vfs")).execute("vfs-info x")
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].is_error)

    def test_vfs_name_for_window(self):
        """Имя VFS для заголовка окна берётся из VFS."""
        self.assertEqual(Shell(empty_vfs("disk")).vfs_name, "disk")


class OpenVfsTests(VfsTestCase):
    """Проверки загрузки VFS при запуске (параметр --vfs)."""

    def test_without_vfs_param(self):
        """Без --vfs — пустая VFS без сообщений."""
        vfs, messages = open_vfs(Config())
        self.assertEqual((vfs.count(), messages), ((0, 0), []))

    def test_valid_vfs(self):
        """Корректный файл загружается, ошибок нет."""
        vfs, messages = open_vfs(Config(example("deep.xml")))
        self.assertEqual((vfs.name, vfs.count()), ("deep", (6, 5)))
        self.assertEqual(messages, [])

    def test_error_gives_empty_vfs_and_message(self):
        """При ошибке — пустая VFS и красное сообщение."""
        vfs, messages = open_vfs(Config("no/such/disk.xml"))
        self.assertEqual(vfs.count(), (0, 0))
        self.assertEqual(messages, [Message(
            "ошибка VFS: no/such/disk.xml: файл не найден", True)])
        self.assertIn("не загружена", vfs.source_text)

    def test_error_goes_after_debug_and_before_script(self):
        """Ошибка VFS стоит после [debug] и до диалога скрипта."""
        script = os.path.join(self.tmp.name, "s.emu")
        with open(script, "w", encoding="utf-8") as file:
            file.write("vfs-info\n")
        config = Config(example("broken.xml"), script)
        vfs, messages = open_vfs(config)
        startup = build_startup(config, Shell(vfs), messages)
        texts = [message.text for message in startup]
        error_index = next(i for i, m in enumerate(startup) if m.is_error)
        self.assertTrue(texts[error_index - 1].startswith("[debug]"))
        self.assertIn("vfs-info", texts[error_index + 1])


if __name__ == "__main__":
    unittest.main()
