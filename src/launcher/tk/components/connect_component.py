import typing
import tkinter as tk
from ttkbootstrap import ttk
from launcher.tk.components.tk_component import Component
from launcher.tk.page.page_manager import PageManager
from launcher.tk.launcher_user import LauncherUser


class ConnectWidgets(typing.NamedTuple):
    server_ip_entry: ttk.Entry
    connect_button: ttk.Button


class ConnectVars(typing.NamedTuple):
    ip_entry_var: tk.StringVar


class ConnectComponent(Component):
    def __init__(self, parent: ttk.Frame, page_manager: PageManager) -> None:
        super().__init__(parent, "Connect")
        self.page_manager: PageManager = page_manager
        self.vars: ConnectVars = create_vars()
        self.widgets: ConnectWidgets = self.create_widgets()

        self.widgets.server_ip_entry.pack(expand=True)
        self.widgets.connect_button.pack(expand=True)

    def create_widgets(self) -> ConnectWidgets:
        server_ip_entry: ttk.Entry = ttk.Entry(self.frame, textvariable=self.vars.ip_entry_var)
        connect_button: ttk.Button = ttk.Button(self.frame, text="Connect", command=self.handle_connect)
        return ConnectWidgets(server_ip_entry, connect_button)

    def handle_connect(self) -> None:
        LauncherUser.get_client().set_ip_address(self.vars.ip_entry_var.get())
        is_connect_successful: bool = LauncherUser.get_client().start()

        if is_connect_successful:
            self.page_manager.show_page("ServerPage")
        else:
            # TODO: add error label to show when the client cannot connect
            pass


def create_vars() -> ConnectVars:
    ip_entry_var: tk.StringVar = tk.StringVar()
    return ConnectVars(ip_entry_var)
