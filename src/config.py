"""Параметры командной строки эмулятора и их отладочный вывод."""

import argparse
import os
from dataclasses import dataclass
from typing import Optional

DEFAULT_VFS_NAME = "vfs"
NOT_SET = "<не задан>"
DEBUG_PREFIX = "[debug]"


@dataclass
class Config:
    """Параметры запуска эмулятора (None — параметр не задан)."""

    vfs_path: Optional[str] = None
    script_path: Optional[str] = None

    @property
    def vfs_name(self):
        """Имя VFS для заголовка окна: имя файла без расширения."""
        if not self.vfs_path:
            return DEFAULT_VFS_NAME
        base = os.path.basename(os.path.normpath(self.vfs_path))
        name = os.path.splitext(base)[0]
        return name or DEFAULT_VFS_NAME


def build_parser():
    """Создаёт разборщик аргументов командной строки."""
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="Эмулятор командной оболочки UNIX-подобной ОС.",
        allow_abbrev=False,
    )
    parser.add_argument(
        "--vfs", metavar="ПУТЬ",
        help="путь к физическому расположению VFS")
    parser.add_argument(
        "--script", metavar="ПУТЬ",
        help="путь к стартовому скрипту")
    return parser


def parse_args(argv):
    """Разбирает список аргументов и возвращает Config.

    При неверных аргументах argparse печатает справку об ошибке
    и завершает программу с кодом 2.
    """
    args = build_parser().parse_args(argv)
    return Config(vfs_path=args.vfs, script_path=args.script)


def debug_lines(config):
    """Возвращает строки отладочного вывода всех параметров запуска."""
    return [
        f"{DEBUG_PREFIX} параметры запуска:",
        f"{DEBUG_PREFIX}   --vfs    = {config.vfs_path or NOT_SET}",
        f"{DEBUG_PREFIX}   --script = {config.script_path or NOT_SET}",
        f"{DEBUG_PREFIX}   имя VFS  = {config.vfs_name}",
    ]
