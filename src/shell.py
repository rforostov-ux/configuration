import getpass
import socket
from dataclasses import dataclass

from cmd_parser import ParseError, parse

MAX_CD_ARGS = 1
MAX_EXIT_ARGS = 1
DEFAULT_EXIT_CODE = 0


@dataclass
class Message:
    """Строка вывода: текст и признак ошибки"""

    text: str
    is_error: bool = False


def stub_output(name, args):
    """Вывод команды-заглушки: имя команды и каждый её аргумент.

    Каждый аргумент печатается отдельной строкой в кавычках, чтобы
    были видны пробелы внутри аргумента и пустые аргументы.
    """
    if not args:
        return [Message(f"{name}: заглушка, аргументов нет")]
    lines = [Message(f"{name}: заглушка, аргументов: {len(args)}")]
    for number, arg in enumerate(args, start=1):
        lines.append(Message(f'  {number}) "{arg}"'))
    return lines


class Shell:
    """Оболочка: хранит состояние и выполняет введённые строки."""

    def __init__(self, vfs_name):
        """Создаёт оболочку для виртуальной ФС с именем vfs_name."""
        self.vfs_name = vfs_name
        self.prompt = f"{getpass.getuser()}@{socket.gethostname()}:~$ "
        self.exit_code = None
        self.commands = {
            "ls": self.cmd_ls,
            "cd": self.cmd_cd,
            "exit": self.cmd_exit,
        }

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
        return handler(args)

    def cmd_ls(self, args):
        """Заглушка ls: печатает имя команды и аргументы."""
        return stub_output("ls", args)

    def cmd_cd(self, args):
        """Заглушка cd: печатает имя команды и аргументы."""
        if len(args) > MAX_CD_ARGS:
            return [Message("cd: слишком много аргументов", True)]
        return stub_output("cd", args)

    def cmd_exit(self, args):
        """Команда exit [код]: завершает работу оболочки."""
        if len(args) > MAX_EXIT_ARGS:
            return [Message("exit: слишком много аргументов", True)]
        code = DEFAULT_EXIT_CODE
        if args:
            try:
                code = int(args[0])
            except ValueError:
                text = f"exit: {args[0]}: требуется числовой аргумент"
                return [Message(text, True)]
        self.exit_code = code
        return []