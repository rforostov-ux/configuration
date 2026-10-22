"""Точка входа.

Запуск: python src/main.py [--vfs ПУТЬ] [--script ПУТЬ].
"""

import sys

import gui
from config import parse_args
from shell import Shell
from startup import build_startup, open_vfs

EXIT_OK = 0


def main():
    """Разбирает параметры, загружает VFS, запускает окно."""
    config = parse_args(sys.argv[1:])
    vfs, vfs_messages = open_vfs(config)
    shell = Shell(vfs)
    gui.run(shell, build_startup(config, shell, vfs_messages))
    sys.exit(shell.exit_code or EXIT_OK)


if __name__ == "__main__":
    main()
