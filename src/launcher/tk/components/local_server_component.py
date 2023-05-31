import typing
import tkinter as tk
from ttkbootstrap import ttk

from launcher.tk.components.tk_component import Component


class LocalServerWidgets(typing.NamedTuple):
    server_online_label: ttk.Label
    start_server_button: ttk.Button
    stop_server_button: ttk.Button


class LocalServerVars(typing.NamedTuple):
    server_online_text_var: tk.StringVar
    is_server_online_var: tk.BooleanVar


class LocalServerComponent(Component):
    def __init__(self, parent: ttk.Frame) -> None:
        super().__init__(parent, "Local Server")
        self.vars: LocalServerVars = self.create_vars()
        self.widgets: LocalServerWidgets = self.create_widgets()

        self.widgets.server_online_label.pack(expand=True)
        self.widgets.start_server_button.pack(expand=True)

    def create_vars(self) -> LocalServerVars:
        is_server_online_var: tk.BooleanVar = tk.BooleanVar(value=self.is_server_online())
        server_online_text_var: tk.StringVar = tk.StringVar(value=get_online_label_value(is_server_online_var.get()))
        return LocalServerVars(server_online_text_var, is_server_online_var)

    def create_widgets(self) -> LocalServerWidgets:
        foreground_color: str = get_online_label_color(self.vars.is_server_online_var.get())
        server_online_label: ttk.Label = ttk.Label(self.frame, textvariable=self.vars.server_online_text_var,
                                                   foreground=foreground_color)
        start_server_button: ttk.Button = ttk.Button(self.frame, text="Start Server",
                                                     command=lambda: self.handle_start_server())

        stop_server_button: ttk.Button = ttk.Button(self.frame, text="Stop Server",
                                                    command=lambda: self.handle_stop_server())
        return LocalServerWidgets(server_online_label, start_server_button, stop_server_button)

    def is_server_online(self) -> bool:
        # FIXME: Implement Me
        return False

    def handle_start_server(self):
        if self.vars.is_server_online_var.get(): return
        if not self.is_server_online(): return
        self.vars.is_server_online_var.set(True)
        self.vars.server_online_text_var.set(get_online_label_value(True))
        self.widgets.server_online_label.config(foreground=get_online_label_color(True))
        self.widgets.start_server_button.pack_forget()
        self.widgets.stop_server_button.pack(expand=True)

    def handle_stop_server(self) -> None:
        if not self.vars.is_server_online_var.get(): return
        self.vars.is_server_online_var.set(False)
        self.vars.server_online_text_var.set(get_online_label_value(False))
        self.widgets.server_online_label.config(foreground=get_online_label_color(False))
        self.widgets.stop_server_button.pack_forget()
        self.widgets.start_server_button.pack(expand=True)


def get_online_label_value(is_online: bool) -> str:
    server_status: str = "Online" if is_online else "Offline"
    return f"server is {server_status}"


def get_online_label_color(is_online: bool) -> str:
    return "green" if is_online else "red"
