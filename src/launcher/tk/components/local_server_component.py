import tkinter as tk
import typing
from _thread import start_new_thread

from ttkbootstrap import ttk

from launcher.tk.components.tk_component import Component
from launcher.tk.global_vars import GlobalUserVars
from network.server.chess_server import ChessServer


class LocalServerWidgets(typing.NamedTuple):
    server_online_label: ttk.Label
    start_server_button: ttk.Button
    stop_server_button: ttk.Button
    refresh_server_button: ttk.Button
    error_label: ttk.Label
    button_frame: ttk.Frame
    ip_label: ttk.Label


class LocalServerVars(typing.NamedTuple):
    server_online_text_var: tk.StringVar
    is_server_online_var: tk.BooleanVar
    error_var: tk.StringVar


class LocalServerComponent(Component):
    def __init__(self, parent: ttk.Frame, started_server: tk.BooleanVar) -> None:
        super().__init__(parent, "Local Server")
        self.started_server: tk.BooleanVar = started_server
        self.vars: LocalServerVars = self.create_vars()
        self.widgets: LocalServerWidgets = self.create_widgets()

        self.widgets.start_server_button.pack(side=tk.LEFT, expand=True)
        self.widgets.refresh_server_button.pack(side=tk.LEFT, expand=True)

        self.widgets.server_online_label.pack(expand=True)
        self.widgets.button_frame.pack(expand=True)

    def create_vars(self) -> LocalServerVars:
        is_server_online_var: tk.BooleanVar = tk.BooleanVar(value=False)
        server_online_text_var: tk.StringVar = tk.StringVar(value=get_online_label_value(is_server_online_var.get()))
        error_var: tk.StringVar = tk.StringVar()
        is_server_online_var.trace_add("write", lambda v, i, m: self.is_server_online_callback())
        return LocalServerVars(server_online_text_var, is_server_online_var, error_var)

    def create_widgets(self) -> LocalServerWidgets:
        foreground_color: str = get_online_label_color(self.vars.is_server_online_var.get())
        server_online_label: ttk.Label = ttk.Label(self.frame, textvariable=self.vars.server_online_text_var,
                                                   foreground=foreground_color)
        buttons_frame: ttk.Frame = ttk.Frame(self.frame)
        start_server_button: ttk.Button = ttk.Button(buttons_frame, text="Start Server",
                                                     command=lambda: self.handle_start_server())
        stop_server_button: ttk.Button = ttk.Button(buttons_frame, text="Stop Server",
                                                    command=lambda: self.handle_stop_server())
        refresh: ttk.Button = ttk.Button(buttons_frame, text="refresh", command=lambda:
                                         self.vars.is_server_online_var.set(ChessServer.is_local_server_online()))
        error_label: ttk.Label = ttk.Label(self.frame, textvariable=self.vars.error_var)
        GlobalUserVars.get_server_disconnect().trace_add("write", lambda v, i, m: self.handle_refresh_server())
        ip_label: ttk.Label = ttk.Label(self.frame, text=f"server ip: {ChessServer.get_host_ipv4()}")
        return LocalServerWidgets(server_online_label, start_server_button, stop_server_button,
                                  refresh, error_label, buttons_frame, ip_label)

    def handle_refresh_server(self) -> None:
        self.vars.is_server_online_var.set(ChessServer.is_local_server_online())

    def handle_start_server(self):
        self.handle_refresh_server()
        if self.vars.is_server_online_var.get():
            self.started_server.set(False)
            return
        if not ChessServer.get().start(): return
        start_new_thread(ChessServer.get().run, (False,))
        self.started_server.set(True)
        self.vars.is_server_online_var.set(True)

    def handle_stop_server(self) -> None:
        if not self.vars.is_server_online_var.get(): return
        ChessServer.get().shut_down()
        self.started_server.set(False)
        self.vars.is_server_online_var.set(False)

    def is_server_online_callback(self) -> None:
        if self.vars.is_server_online_var.get():
            self.widgets.server_online_label.configure(foreground="green")
            self.vars.server_online_text_var.set(get_online_label_value(True))
            self.widgets.server_online_label.pack_forget()
            self.widgets.start_server_button.pack_forget()
            self.widgets.refresh_server_button.pack_forget()
            self.widgets.button_frame.pack_forget()

            self.widgets.server_online_label.pack(expand=True)
            self.widgets.ip_label.pack(expand=True)
            if self.started_server.get():
                self.widgets.stop_server_button.pack(expand=True)
                self.widgets.button_frame.pack(expand=True)

        else:
            self.vars.server_online_text_var.set(get_online_label_value(False))
            self.widgets.server_online_label.configure(foreground="red")
            self.widgets.start_server_button.pack(side=tk.LEFT, expand=True)
            self.widgets.refresh_server_button.pack(side=tk.LEFT, expand=True)
            self.widgets.button_frame.pack(expand=True)
            self.widgets.stop_server_button.pack_forget()
            self.widgets.ip_label.pack_forget()


def get_online_label_value(is_online: bool) -> str:
    server_status: str = "Online" if is_online else "Offline"
    return f"server is {server_status}"


def get_online_label_color(is_online: bool) -> str:
    return "green" if is_online else "red"
