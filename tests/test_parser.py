"""Тесты парсера командной строки."""

import os
import unittest
from unittest import mock

from cmd_parser import ParseError, parse

TEST_ENV = {"HOME": "/home/user", "USER": "user", "DIR": "my dir"}


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
class ParseTests(unittest.TestCase):
    """Проверки функции parse (переменные окружения подменены)."""

    def test_plain_words(self):
        """Обычные слова делятся по пробелам."""
        self.assertEqual(parse("ls -l /tmp"), ["ls", "-l", "/tmp"])

    def test_extra_spaces(self):
        """Лишние пробелы игнорируются."""
        self.assertEqual(parse("  ls   -l  "), ["ls", "-l"])

    def test_empty_line(self):
        """Пустая строка даёт пустой список."""
        self.assertEqual(parse(""), [])
        self.assertEqual(parse("   "), [])

    def test_env_var(self):
        """$HOME раскрывается значением переменной."""
        self.assertEqual(parse("cd $HOME"), ["cd", "/home/user"])

    def test_env_var_in_braces(self):
        """${USER}_x раскрывается и склеивается с текстом."""
        self.assertEqual(parse("ls ${USER}_x"), ["ls", "user_x"])

    def test_env_var_in_double_quotes(self):
        """В двойных кавычках подстановка работает, пробелы целы."""
        self.assertEqual(parse('cd "$DIR/a"'), ["cd", "my dir/a"])

    def test_single_quotes_no_expansion(self):
        """В одинарных кавычках подстановки нет."""
        self.assertEqual(parse("ls '$HOME'"), ["ls", "$HOME"])

    def test_undefined_var_is_dropped(self):
        """Неопределённая переменная вне кавычек исчезает."""
        self.assertEqual(parse("ls $NOPE end"), ["ls", "end"])

    def test_undefined_var_in_quotes_is_empty_word(self):
        """В кавычках неопределённая переменная даёт пустой аргумент."""
        self.assertEqual(parse('ls "$NOPE"'), ["ls", ""])

    def test_empty_quotes(self):
        """Пустые кавычки — это пустой аргумент."""
        self.assertEqual(parse('ls ""'), ["ls", ""])

    def test_lone_dollar(self):
        """Одиночный '$' остаётся как есть."""
        self.assertEqual(parse("ls $ a"), ["ls", "$", "a"])

    def test_unclosed_double_quote(self):
        """Незакрытая двойная кавычка — ошибка."""
        with self.assertRaises(ParseError):
            parse('ls "abc')

    def test_unclosed_single_quote(self):
        """Незакрытая одинарная кавычка — ошибка."""
        with self.assertRaises(ParseError):
            parse("ls 'abc")

    def test_unclosed_brace(self):
        """Нет закрывающей '}' — ошибка."""
        with self.assertRaises(ParseError):
            parse("ls ${HOME")

    def test_bad_var_name(self):
        """Пустое или неверное имя в ${} — ошибка."""
        with self.assertRaises(ParseError):
            parse("ls ${}")
        with self.assertRaises(ParseError):
            parse("ls ${1x}")


if __name__ == "__main__":
    unittest.main()