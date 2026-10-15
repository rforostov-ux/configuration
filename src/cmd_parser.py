"""Парсер командной строки: строка -> список слов.

Раскрывает переменные окружения реальной ОС ($HOME, ${HOME}) и
учитывает 'одинарные' и "двойные" кавычки. Неэкранированный
'#' в начале слова начинает комментарий до конца строки.
"""

import os

NOT_FOUND = -1
SPACES = " \t"
COMMENT = "#"
SINGLE_QUOTE = "'"
DOUBLE_QUOTE = '"'
DOLLAR = "$"
UNDERSCORE = "_"
QUOTES = SINGLE_QUOTE + DOUBLE_QUOTE


class ParseError(Exception):
    """Синтаксическая ошибка во введённой строке."""


def is_name_char(char):
    """Проверяет, может ли символ входить в имя переменной."""
    return char.isalnum() or char == UNDERSCORE


def read_var_name(line, pos):
    """Читает имя переменной, начиная с pos (сразу после '$').

    Поддерживаются формы $NAME и ${NAME}. Возвращает пару
    (имя, позиция_после_имени). Имя пустое, если после '$' его нет.
    """
    if line.startswith("{", pos):
        end = line.find("}", pos)
        if end == NOT_FOUND:
            raise ParseError("нет закрывающей '}'")
        name = line[pos + 1:end]
        if not name.isidentifier():
            raise ParseError("${" + name + "}: неверная подстановка")
        return name, end + 1
    end = pos
    while end < len(line) and is_name_char(line[end]):
        end += 1
    return line[pos:end], end


def expand_var(line, pos):
    """Раскрывает переменную; line[pos] == '$'.

    Возвращает (значение, позиция_после_переменной). Неопределённая
    переменная даёт пустую строку, одиночный '$' остаётся '$'.
    """
    name, end = read_var_name(line, pos + 1)
    if not name:
        return "$", end
    return os.environ.get(name, ""), end


def read_single_quoted(line, pos):
    """Читает текст в 'одинарных кавычках' без подстановок.

    line[pos] == "'". Возвращает (текст, позиция_после_кавычки).
    """
    end = line.find("'", pos + 1)
    if end == NOT_FOUND:
        raise ParseError("незакрытая одинарная кавычка")
    return line[pos + 1:end], end + 1


def read_double_quoted(line, pos):
    """Читает текст в "двойных кавычках" с раскрытием переменных.

    line[pos] == '"'. Возвращает (текст, позиция_после_кавычки).
    """
    text = ""
    pos += 1
    while pos < len(line) and line[pos] != DOUBLE_QUOTE:
        if line[pos] == DOLLAR:
            value, pos = expand_var(line, pos)
            text += value
        else:
            text += line[pos]
            pos += 1
    if pos >= len(line):
        raise ParseError("незакрытая двойная кавычка")
    return text, pos + 1


def read_fragment(line, pos):
    """Читает один фрагмент слова, начиная с pos.

    Фрагмент — это текст в кавычках, переменная или обычный символ.
    Возвращает (текст, позиция_после_фрагмента).
    """
    char = line[pos]
    if char == SINGLE_QUOTE:
        return read_single_quoted(line, pos)
    if char == DOUBLE_QUOTE:
        return read_double_quoted(line, pos)
    if char == DOLLAR:
        return expand_var(line, pos)
    return char, pos + 1


def is_comment_start(char, current):
    """Проверяет, начинается ли комментарий: '#' в начале слова."""
    return char == COMMENT and current is None


def append_fragment(current, text, char):
    """Добавляет фрагмент к текущему слову и возвращает слово.

    Пустой фрагмент слова не начинает, кроме пустых кавычек: так
    "" даёт пустой аргумент, а неопределённая $VAR — ничего.
    """
    if text or char in QUOTES:
        return (current or "") + text
    return current


def parse(line):
    """Разбивает строку на слова с учётом кавычек и переменных.

    Пробелы вне кавычек разделяют слова. Пустое слово получается
    только из пустых кавычек: "" даёт [""], а $НЕТ_ТАКОЙ даёт [].
    Комментарий ('#' в начале слова) отбрасывается до конца строки.
    Бросает ParseError, если строка составлена неверно.
    """
    words = []
    current = None
    pos = 0
    while pos < len(line):
        char = line[pos]
        if is_comment_start(char, current):
            break
        if char in SPACES:
            if current is not None:
                words.append(current)
                current = None
            pos += 1
            continue
        text, pos = read_fragment(line, pos)
        current = append_fragment(current, text, char)
    if current is not None:
        words.append(current)
    return words
