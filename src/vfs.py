"""Виртуальная файловая система (VFS): модель в памяти и загрузка из XML.

Формат XML:

    <vfs>
      <dir name="home">
        <file name="notes.txt">текст файла</file>
        <file name="logo.png" encoding="base64">iVBORw0KGgo=</file>
      </dir>
    </vfs>

Корневой элемент <vfs> соответствует каталогу "/". VFS читается один
раз при запуске, дальше все операции идут только в памяти: XML-файл на
диске никогда не изменяется.
"""

import base64
import binascii
import xml.etree.ElementTree as element_tree
from dataclasses import dataclass, field
from typing import Dict, Optional, Union

ROOT_TAG = "vfs"
DIR_TAG = "dir"
FILE_TAG = "file"
NAME_ATTR = "name"
ENCODING_ATTR = "encoding"
BASE64 = "base64"
TEXT_ENCODING = "utf-8"
SEPARATOR = "/"
ROOT_PATH = "/"
RESERVED_NAMES = (".", "..")
NOT_SET = "<не задан>"


class VfsError(Exception):
    """VFS не удалось загрузить: нет файла, неверный XML или структура."""


@dataclass
class VfsFile:
    """Файл VFS: имя и содержимое в байтах."""

    name: str
    data: bytes = b""
    binary: bool = False


@dataclass
class VfsDir:
    """Каталог VFS: имя и словарь «имя -> файл или каталог»."""

    name: str
    children: Dict[str, Union["VfsDir", VfsFile]] = field(
        default_factory=dict)


@dataclass
class Vfs:
    """Загруженная VFS: имя, источник и корневой каталог."""

    name: str
    root: VfsDir
    source: Optional[str] = None

    def count(self):
        """Возвращает пару (число каталогов, число файлов) без корня."""
        return count_nodes(self.root)

    @property
    def source_text(self):
        """Источник VFS для вывода пользователю."""
        return self.source or NOT_SET


def count_nodes(directory):
    """Считает каталоги и файлы внутри каталога (рекурсивно)."""
    dirs, files = 0, 0
    for node in directory.children.values():
        if isinstance(node, VfsDir):
            sub_dirs, sub_files = count_nodes(node)
            dirs += 1 + sub_dirs
            files += sub_files
        else:
            files += 1
    return dirs, files


def empty_vfs(name, source=None):
    """Создаёт пустую VFS, в которой есть только корневой каталог."""
    return Vfs(name, VfsDir(""), source)


def join_path(parent, name):
    """Склеивает путь каталога и имя: ("/", "a") -> "/a"."""
    if parent == ROOT_PATH:
        return ROOT_PATH + name
    return parent + SEPARATOR + name


def read_xml(path):
    """Читает и разбирает XML-файл, возвращает корневой элемент."""
    try:
        with open(path, "rb") as file:
            data = file.read()
    except FileNotFoundError as error:
        raise VfsError(f"{path}: файл не найден") from error
    except OSError as error:
        raise VfsError(f"{path}: {error.strerror}") from error
    try:
        return element_tree.fromstring(data)
    except element_tree.ParseError as error:
        line = error.position[0]
        text = f"{path}: неверный формат XML (строка {line})"
        raise VfsError(text) from error


def load_vfs(path, name):
    """Загружает VFS из XML-файла path. Бросает VfsError при ошибке."""
    element = read_xml(path)
    if element.tag != ROOT_TAG:
        raise VfsError(f"неизвестный элемент <{element.tag}>")
    root = VfsDir("")
    fill_dir(root, element, ROOT_PATH)
    return Vfs(name, root, path)


def fill_dir(directory, element, path):
    """Заполняет каталог directory узлами из XML-элемента element."""
    for child in element:
        node = build_node(child, path)
        if node.name in directory.children:
            raise VfsError(f"каталог {path}: повторяется имя {node.name}")
        directory.children[node.name] = node


def build_node(element, parent_path):
    """Создаёт файл или каталог из XML-элемента."""
    if element.tag not in (DIR_TAG, FILE_TAG):
        raise VfsError(f"неизвестный элемент <{element.tag}>")
    name = read_name(element, parent_path)
    path = join_path(parent_path, name)
    if element.tag == DIR_TAG:
        directory = VfsDir(name)
        fill_dir(directory, element, path)
        return directory
    return build_file(element, name, path)


def read_name(element, parent_path):
    """Читает и проверяет атрибут name у элемента."""
    name = element.get(NAME_ATTR)
    if name is None:
        raise VfsError(f"каталог {parent_path}: элемент <{element.tag}> "
                       f"без атрибута {NAME_ATTR}")
    if not name or SEPARATOR in name or name in RESERVED_NAMES:
        raise VfsError(f"каталог {parent_path}: недопустимое имя «{name}»")
    return name


def build_file(element, name, path):
    """Создаёт файл: текст как есть или двоичные данные из base64."""
    if len(element):
        raise VfsError(f"файл {path}: внутри файла не может быть элементов")
    text = element.text or ""
    encoding = element.get(ENCODING_ATTR)
    if encoding is None:
        return VfsFile(name, text.encode(TEXT_ENCODING))
    if encoding != BASE64:
        raise VfsError(f"файл {path}: неизвестная кодировка {encoding}")
    try:
        data = base64.b64decode("".join(text.split()), validate=True)
    except (binascii.Error, ValueError) as error:
        raise VfsError(f"файл {path}: неверные данные base64") from error
    return VfsFile(name, data, binary=True)


CURRENT_DIR = "."
PARENT_DIR = ".."
NOT_FOUND = "нет такого файла или каталога"
NOT_A_DIR = "не каталог"


class VfsPathError(Exception):
    """Путь в VFS не найден или проходит через файл."""


def is_dir(node):
    """Проверяет, что узел — каталог."""
    return isinstance(node, VfsDir)


def path_from_names(names):
    """Собирает абсолютный путь из списка имён: [] -> "/"."""
    return ROOT_PATH + SEPARATOR.join(names)


def step(root, stack, part):
    """Делает один шаг по пути: stack — список пар (имя, узел)."""
    current = stack[-1][1] if stack else root
    if not is_dir(current):
        raise VfsPathError(NOT_A_DIR)
    if part == PARENT_DIR:
        if stack:
            stack.pop()
    elif part != CURRENT_DIR:
        node = current.children.get(part)
        if node is None:
            raise VfsPathError(NOT_FOUND)
        stack.append((part, node))


def resolve(vfs, cwd, path):
    """Находит узел по пути относительно текущего каталога cwd.

    Путь может быть абсолютным ("/home/user") или относительным
    ("user/notes.txt"), "." — текущий каталог, ".." — родитель (выше
    корня подняться нельзя). Возвращает пару (узел, абсолютный путь).
    Бросает VfsPathError, если пути нет или он проходит через файл.
    """
    if not path:
        raise VfsPathError(NOT_FOUND)
    stack = []
    if not path.startswith(SEPARATOR):
        for part in cwd.split(SEPARATOR):
            if part:
                step(vfs.root, stack, part)
    for part in path.split(SEPARATOR):
        if part:
            step(vfs.root, stack, part)
    node = stack[-1][1] if stack else vfs.root
    return node, path_from_names([name for name, _ in stack])
