"""Графический интерфейс: окно в виде терминала.

Окно не выполняет команды само: оно передаёт строку в Shell
и показывает полученные сообщения.
"""

import tkinter as tk

WINDOW_SIZE = "800x500"
FONT = ("Consolas", 12)
BG_COLOR = "black"
TEXT_COLOR = "white"
ERROR_COLOR = "red"
NORMAL_TAG = "normal"
ERROR_TAG = "error"
BUTTON_TEXT = "Выполнить"


class ShellWindow:
    """Окно эмулятора: поле вывода сверху, ввод и кнопка снизу."""

    def __init__(self, root, shell, startup=()):
        """Создаёт окно и показывает стартовые сообщения."""
        self.root = root
        self.shell = shell
        root.title(f"Эмулятор оболочки — VFS: {shell.vfs_name}")
        root.geometry(WINDOW_SIZE)
        self.output = self._create_output()
        self.entry = self._create_input_row()
        self.print_line("Эмулятор оболочки. Для выхода введите exit.")
        self.print_messages(startup)

    def _create_output(self):
        """Создаёт поле вывода, доступное только для чтения."""
        output = tk.Text(self.root, bg=BG_COLOR, fg=TEXT_COLOR,
                         font=FONT, state="disabled")
        output.pack(fill="both", expand=True)
        output.tag_config(NORMAL_TAG, foreground=TEXT_COLOR)
        output.tag_config(ERROR_TAG, foreground=ERROR_COLOR)
        return output

    def _create_input_row(self):
        """Создаёт нижнюю строку: поле ввода и кнопку «Выполнить».

        Команду запускает и Enter в поле ввода, и нажатие кнопки.
        Возвращает поле ввода.
        """
        row = tk.Frame(self.root, bg=BG_COLOR)
        row.pack(fill="x")
        button = tk.Button(row, text=BUTTON_TEXT, font=FONT,
                           command=self.run_entered)
        button.pack(side="right")
        entry = tk.Entry(row, bg=BG_COLOR, fg=TEXT_COLOR,
                         insertbackground=TEXT_COLOR, font=FONT)
        entry.pack(side="left", fill="x", expand=True)
        entry.bind("<Return>", self.on_enter)
        entry.focus()
        return entry

    def print_line(self, text, tag=NORMAL_TAG):
        """Добавляет строку в конец поля вывода и прокручивает вниз."""
        self.output.config(state="normal")
        self.output.insert(tk.END, text + "\n", tag)
        self.output.config(state="disabled")
        self.output.see(tk.END)

    def print_messages(self, messages):
        """Печатает сообщения оболочки; ошибки выделяются цветом."""
        for message in messages:
            tag = ERROR_TAG if message.is_error else NORMAL_TAG
            self.print_line(message.text, tag)

    def on_enter(self, _event):
        """Обработчик Enter: выполняет введённую строку."""
        self.run_entered()

    def run_entered(self):
        """Выполняет строку из поля ввода и показывает результат.

        Вызывается по Enter и по кнопке «Выполнить».
        """
        line = self.entry.get()
        self.entry.delete(0, tk.END)
        self.print_line(self.shell.prompt + line)
        self.print_messages(self.shell.execute(line))
        if self.shell.exit_code is not None:
            self.root.destroy()
            return
        self.entry.focus()


def run(shell, startup=()):
    """Создаёт окно, показывает стартовые сообщения, запускает цикл.

    Если стартовый скрипт уже выполнил exit, окно сразу закрывается.
    """
    root = tk.Tk()
    ShellWindow(root, shell, startup)
    if shell.exit_code is None:
        root.mainloop()
    else:
        root.destroy()
