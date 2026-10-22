"""Логика оболочки: разбор строки и выполнение команд.

Модуль ничего не знает про окно. Результат команды возвращается
списком сообщений, а показывает их уже модуль gui. Оболочка работает
с VFS, загруженной в память (модуль vfs), и помнит текущий каталог.
"""

import getpass
import socket
from dataclasses import dataclass

from cmd_parser import ParseError, parse
from vfs import ROOT_PATH, VfsPathError, is_dir, resolve

MAX_LS_ARGS = 1
MAX_CD_ARGS = 1
MAX_EXIT_ARGS = 1
MAX_VFS_INFO_ARGS = 0
FILE_ARGS = 1
OPTION_WITH_VALUE_ARGS = 2
DEFAULT_EXIT_CODE = 0
DEFAULT_TAIL_LINES = 10
MIN_TAIL_LINES = 0
COUNT_OPTION = "-n"
OPTION_PREFIX = "-"
DIR_SUFFIX = "/"
TEXT_ENCODING = "utf-8"
NEED_FILE = "требуется один аргумент — файл"


class CommandError(Exception):
    """Ошибка выполнения команды; текст выводится после имени команды."""


@dataclass
class Message:
    """Строка вывода: текст и признак ошибки (как struct в C++)."""

    text: str
    is_error: bool = False


def has_error(messages):
    """Проверяет, есть ли среди сообщений хотя бы одна ошибка."""
    return any(message.is_error for message in messages)


def check_not_option(arg):
    """Ключи вида -x командами ls, cd, tac не поддерживаются."""
    if arg.startswith(OPTION_PREFIX) and arg != OPTION_PREFIX:
        raise CommandError(f"неизвестный ключ {arg}")


def parse_count(text):
    """Разбирает число строк для tail -n: целое число не меньше 0."""
    try:
        count = int(text)
    except ValueError:
        count = None
    if count is None or count < MIN_TAIL_LINES:
        raise CommandError(f"{COUNT_OPTION} {text}: требуется "
                           "неотрицательное число")
    return count


def parse_tail_args(args):
    """Разбирает аргументы tail [-n N] файл. Возвращает (N, файл)."""
    count = DEFAULT_TAIL_LINES
    if args and args[0] == COUNT_OPTION:
        if len(args) < OPTION_WITH_VALUE_ARGS:
            raise CommandError(f"{COUNT_OPTION}: требуется "
                               "неотрицательное число")
        count = parse_count(args[1])
        args = args[OPTION_WITH_VALUE_ARGS:]
    if len(args) != FILE_ARGS:
        raise CommandError(NEED_FILE)
    check_not_option(args[0])
    return count, args[0]


class Shell:
    """Оболочка: хранит состояние и выполняет введённые строки."""

    def __init__(self, vfs):
        """Создаёт оболочку для загруженной VFS (объект vfs.Vfs)."""
        self.vfs = vfs
        self.cwd = ROOT_PATH
        self.user_host = f"{getpass.getuser()}@{socket.gethostname()}"
        self.exit_code = None
        self.commands = {
            "ls": self.cmd_ls,
            "cd": self.cmd_cd,
            "tail": self.cmd_tail,
            "tac": self.cmd_tac,
            "exit": self.cmd_exit,
            "vfs-info": self.cmd_vfs_info,
        }

    @property
    def vfs_name(self):
        """Имя VFS для заголовка окна."""
        return self.vfs.name

    @property
    def prompt(self):
        """Приглашение с текущим каталогом: user@host:/home/user$ ."""
        return f"{self.user_host}:{self.cwd}$ "

    def execute(self, line):
        """Выполняет строку и возвращает список сообщений для вывода."""
        try:
            words = parse(line)
        except ParseError as error:
            return [Message(f"синтаксическая ошибка: {error}", True)]
        if not words:
            return []
        name, args = words[0], words[1:]
        handler = self.commands.get(name)
        if handler is None:
            return [Message(f"{name}: команда не найдена", True)]
        try:
            return handler(args)
        except CommandError as error:
            return [Message(f"{name}: {error}", True)]

    def find(self, path):
        """Находит узел VFS по пути. Возвращает (узел, абсолютный путь)."""
        try:
            return resolve(self.vfs, self.cwd, path)
        except VfsPathError as error:
            raise CommandError(f"{path}: {error}") from error

    def read_lines(self, path):
        """Читает строки текстового файла VFS для tail и tac."""
        check_not_option(path)
        node, _ = self.find(path)
        if is_dir(node):
            raise CommandError(f"{path}: это каталог")
        if node.binary:
            raise CommandError(f"{path}: двоичный файл")
        return node.data.decode(TEXT_ENCODING).splitlines()

    def cmd_ls(self, args):
        """ls [путь]: содержимое каталога; каталоги выводятся с "/"."""
        if len(args) > MAX_LS_ARGS:
            raise CommandError("слишком много аргументов")
        path = args[0] if args else self.cwd
        check_not_option(path)
        node, _ = self.find(path)
        if not is_dir(node):
            return [Message(node.name)]
        return [Message(name + DIR_SUFFIX if is_dir(child) else name)
                for name, child in sorted(node.children.items())]

    def cmd_cd(self, args):
        """cd [путь]: переход в каталог; без аргумента — в корень."""
        if len(args) > MAX_CD_ARGS:
            raise CommandError("слишком много аргументов")
        path = args[0] if args else ROOT_PATH
        check_not_option(path)
        node, absolute = self.find(path)
        if not is_dir(node):
            raise CommandError(f"{path}: не каталог")
        self.cwd = absolute
        return []

    def cmd_tail(self, args):
        """tail [-n N] файл: последние N строк файла (по умолчанию 10)."""
        count, path = parse_tail_args(args)
        lines = self.read_lines(path)
        start = max(len(lines) - count, 0)
        return [Message(line) for line in lines[start:]]

    def cmd_tac(self, args):
        """tac файл: строки файла в обратном порядке."""
        if len(args) != FILE_ARGS:
            raise CommandError(NEED_FILE)
        return [Message(line) for line in reversed(self.read_lines(args[0]))]

    def cmd_exit(self, args):
        """Команда exit [код]: завершает работу оболочки."""
        if len(args) > MAX_EXIT_ARGS:
            raise CommandError("слишком много аргументов")
        code = DEFAULT_EXIT_CODE
        if args:
            try:
                code = int(args[0])
            except ValueError as error:
                raise CommandError(f"{args[0]}: требуется числовой "
                                   "аргумент") from error
        self.exit_code = code
        return []

    def cmd_vfs_info(self, args):
        """Служебная команда vfs-info: имя, источник и размер VFS."""
        if len(args) > MAX_VFS_INFO_ARGS:
            raise CommandError("команда не принимает аргументы")
        dirs, files = self.vfs.count()
        return [
            Message(f"VFS: {self.vfs.name}"),
            Message(f"источник: {self.vfs.source_text}"),
            Message(f"каталогов: {dirs}, файлов: {files}"),
        ]
