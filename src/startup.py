"""Сборка сообщений, которые окно показывает при запуске эмулятора."""

from config import debug_lines
from script import run_script
from shell import Message


def build_startup(config, shell):
    """Возвращает отладочный вывод параметров и результат скрипта.

    Скрипт выполняется только если задан параметр --script.
    """
    startup = [Message(line) for line in debug_lines(config)]
    if config.script_path:
        startup.extend(run_script(shell, config.script_path))
    return startup
