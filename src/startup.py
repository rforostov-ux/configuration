"""Подготовка к запуску: загрузка VFS и стартовые сообщения окна."""

from config import debug_lines
from script import run_script
from shell import Message
from vfs import VfsError, empty_vfs, load_vfs

LOAD_FAILED = "(не загружена из-за ошибки)"


def open_vfs(config):
    """Загружает VFS по параметру --vfs.

    Возвращает пару (VFS, сообщения). Без --vfs создаётся пустая VFS.
    При ошибке загрузки тоже возвращается пустая VFS, а в сообщениях —
    текст ошибки: окно всё равно откроется.
    """
    if not config.vfs_path:
        return empty_vfs(config.vfs_name), []
    try:
        return load_vfs(config.vfs_path, config.vfs_name), []
    except VfsError as error:
        source = f"{config.vfs_path} {LOAD_FAILED}"
        message = Message(f"ошибка VFS: {error}", True)
        return empty_vfs(config.vfs_name, source), [message]


def build_startup(config, shell, vfs_messages=()):
    """Возвращает стартовые сообщения окна.

    Порядок: отладочный вывод параметров, ошибка загрузки VFS (если
    была), диалог стартового скрипта (если задан --script).
    """
    startup = [Message(line) for line in debug_lines(config)]
    startup.extend(vfs_messages)
    if config.script_path:
        startup.extend(run_script(shell, config.script_path))
    return startup
