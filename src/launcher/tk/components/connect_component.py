import tkinter as tk
import typing

from ttkbootstrap import ttk

from config.tk_config import CONNECT_ERROR_WRAP_LEN
from launcher.tk.components.tk_component import Component
from launcher.tk.launcher_user import LauncherUser
from launcher.tk.page.page_manager import PageManager
from network.client.chess_client import ClientConnectResult


class ConnectWidgets(typing.NamedTuple):
    server_ip_entry: ttk.Entry
    error_label: ttk.Label
    connect_button: ttk.Button


class ConnectVars(typing.NamedTuple):
    ip_entry_var: tk.StringVar
    error_var: tk.StringVar


class ConnectComponent(Component):
    def __init__(self, parent: ttk.Frame, page_manager: PageManager, started_server: tk.BooleanVar) -> None:
        super().__init__(parent, "Connect")
        self.started_server: tk.BooleanVar = started_server
        self.page_manager: PageManager = page_manager
        self.vars: ConnectVars = create_vars()
        self.widgets: ConnectWidgets = self.create_widgets()

        self.widgets.server_ip_entry.pack(expand=True)
        self.widgets.error_label.pack(expand=True)
        self.widgets.connect_button.pack(expand=True)

    def create_widgets(self) -> ConnectWidgets:
        server_ip_entry: ttk.Entry = ttk.Entry(self.frame, textvariable=self.vars.ip_entry_var)
        server_ip_entry.bind('<Return>', lambda e: self.handle_connect())
        error_label: ttk.Label = ttk.Label(self.frame, textvariable=self.vars.error_var, foreground="red",
                                           wraplength=CONNECT_ERROR_WRAP_LEN, justify=tk.CENTER)
        connect_button: ttk.Button = ttk.Button(self.frame, text="Connect", command=self.handle_connect)
        return ConnectWidgets(server_ip_entry, error_label, connect_button)

    def handle_connect(self) -> None:
        self.vars.error_var.set("")
        self.widgets.error_label.update()
        server_ip: str = self.vars.ip_entry_var.get()
        if self.started_server.get() and not server_ip:
            server_ip = "127.0.0.1"
        LauncherUser.get_client().set_ip_address(server_ip)
        LauncherUser.get_client().reset_socket()
        is_connect_successful: ClientConnectResult = LauncherUser.get_client().start()
        if is_connect_successful.result:
            self.page_manager.show_page("ServerPage")
        else:
            assert is_connect_successful.error is not None, "error cannot be None here"
            self.vars.error_var.set(is_connect_successful.error.strerror)


def create_vars() -> ConnectVars:
    ip_entry_var: tk.StringVar = tk.StringVar()
    error_var: tk.StringVar = tk.StringVar()
    return ConnectVars(ip_entry_var, error_var)
