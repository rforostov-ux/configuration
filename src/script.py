"""Выполнение стартового скрипта эмулятора.

Скрипт — текстовый файл: одна команда в строке. Пустые строки
пропускаются, строки с '#' — комментарии. Выполнение останавливается
на первой ошибке. Результат — список сообщений, имитирующий диалог:
введённая команда (с приглашением) и её вывод.
"""

from shell import Message, has_error

ENCODING = "utf-8-sig"
LINE_START = 1


class ScriptError(Exception):
    """Файл скрипта не удалось прочитать."""


def read_script(path):
    """Читает файл скрипта и возвращает список его строк.

    Бросает ScriptError, если файла нет, его нельзя открыть
    или он не в кодировке UTF-8.
    """
    try:
        with open(path, encoding=ENCODING) as file:
            return file.read().splitlines()
    except FileNotFoundError as error:
        raise ScriptError(f"{path}: файл не найден") from error
    except UnicodeDecodeError as error:
        raise ScriptError(f"{path}: нужна кодировка UTF-8") from error
    except OSError as error:
        raise ScriptError(f"{path}: {error.strerror}") from error


def stop_message(path, number):
    """Создаёт сообщение об остановке скрипта из-за ошибки."""
    text = f"скрипт остановлен: ошибка в {path}, строка {number}"
    return Message(text, True)


def run_script(shell, path):
    """Выполняет скрипт и возвращает сообщения для показа в окне.

    После первой строки с ошибкой выполнение прекращается и в конец
    добавляется сообщение об ошибке. Команда exit тоже прекращает
    выполнение: код выхода остаётся в shell.exit_code.
    """
    try:
        lines = read_script(path)
    except ScriptError as error:
        return [Message(f"ошибка скрипта: {error}", True)]
    transcript = []
    for number, line in enumerate(lines, start=LINE_START):
        if not line.strip():
            continue
        transcript.append(Message(shell.prompt + line))
        result = shell.execute(line)
        transcript.extend(result)
        if has_error(result):
            transcript.append(stop_message(path, number))
            break
        if shell.exit_code is not None:
            break
    return transcript
