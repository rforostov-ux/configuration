import tkinter as tk

WINDOW_SIZE = "800x500"
FONT = ("Consolas", 12)
BG_COLOR = "black"
TEXT_COLOR = "white"
ERROR_COLOR = "red"
NORMAL_TAG = "normal"
ERROR_TAG = "error"


class ShellWindow:
    """Окно эмулятора: поле вывода сверху и строка ввода снизу."""

    def __init__(self, root, shell):
        """Создаёт элементы окна и привязывает их к оболочке."""
        self.root = root
        self.shell = shell
        root.title(f"Эмулятор оболочки — VFS: {shell.vfs_name}")
        root.geometry(WINDOW_SIZE)
        self.output = self._create_output()
        self.entry = self._create_entry()
        self.print_line("Эмулятор оболочки. Для выхода введите exit.")

    def _create_output(self):
        """Создаёт поле вывода, доступное только для чтения."""
        output = tk.Text(self.root, bg=BG_COLOR, fg=TEXT_COLOR,
                         font=FONT, state="disabled")
        output.pack(fill="both", expand=True)
        output.tag_config(NORMAL_TAG, foreground=TEXT_COLOR)
        output.tag_config(ERROR_TAG, foreground=ERROR_COLOR)
        return output

    def _create_entry(self):
        """Создаёт строку ввода; Enter вызывает on_enter."""
        entry = tk.Entry(self.root, bg=BG_COLOR, fg=TEXT_COLOR,
                         insertbackground=TEXT_COLOR, font=FONT)
        entry.pack(fill="x")
        entry.bind("<Return>", self.on_enter)
        entry.focus()
        return entry

    def print_line(self, text, tag=NORMAL_TAG):
        """Добавляет строку в конец поля вывода и прокручивает вниз."""
        self.output.config(state="normal")
        self.output.insert(tk.END, text + "\n", tag)
        self.output.config(state="disabled")
        self.output.see(tk.END)

    def on_enter(self, _event):
        """Обработчик Enter: выполняет введённую строку."""
        line = self.entry.get()
        self.entry.delete(0, tk.END)
        self.print_line(self.shell.prompt + line)
        for message in self.shell.execute(line):
            tag = ERROR_TAG if message.is_error else NORMAL_TAG
            self.print_line(message.text, tag)
        if self.shell.exit_code is not None:
            self.root.destroy()


def run(shell):
    """Создаёт окно и запускает цикл обработки событий."""
    root = tk.Tk()
    ShellWindow(root, shell)
    root.mainloop()