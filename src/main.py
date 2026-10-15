"""Точка входа.

Запуск: python src/main.py [--vfs ПУТЬ] [--script ПУТЬ].
"""

import sys

import gui
from config import parse_args
from shell import Shell
from startup import build_startup

EXIT_OK = 0


def main():
    """Разбирает параметры, запускает окно, возвращает код выхода."""
    config = parse_args(sys.argv[1:])
    shell = Shell(config.vfs_name)
    gui.run(shell, build_startup(config, shell))
    sys.exit(shell.exit_code or EXIT_OK)


if __name__ == "__main__":
    main()
