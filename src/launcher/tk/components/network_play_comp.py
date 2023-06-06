import tkinter as tk
import typing

from ttkbootstrap import ttk

from launcher.tk.components.tk_component import Component
from launcher.tk.page.page_manager import PageManager


class NetworkPlayWidgets(typing.NamedTuple):
    online: ttk.Button
    offline: ttk.Button


class NetworkPlayVars(typing.NamedTuple):
    is_logged_in: tk.BooleanVar


class NetworkPlayComponent(Component):

    def __init__(self, parent: ttk.Frame, page_manager: PageManager) -> None:
        super().__init__(parent, "Play")
        self.widgets: NetworkPlayWidgets = self.create_widgets(page_manager)
        self.vars: NetworkPlayVars = self.create_vars()
        self.widgets.online.pack(side=tk.LEFT, expand=True, anchor=tk.CENTER)
        self.widgets.offline.pack(side=tk.LEFT, expand=True, anchor=tk.CENTER)

    def create_widgets(self, page_manger: PageManager) -> NetworkPlayWidgets:
        online_button: ttk.Button = ttk.Button(self.frame, text="Online",
                                               command=lambda: page_manger.show_page("OnlinePage"), state=tk.DISABLED)
        offline_button: ttk.Button = ttk.Button(self.frame, text="Offline",
                                                command=lambda: page_manger.show_page("OfflinePage"))
        return NetworkPlayWidgets(online_button, offline_button)

    def create_vars(self) -> NetworkPlayVars:
        is_logged_in: tk.BooleanVar = tk.BooleanVar(value=False)
        is_logged_in.trace_add("write", lambda v, i, m: handle_update_online_button(self.widgets.online, is_logged_in))
        return NetworkPlayVars(is_logged_in)

    def get_vars(self) -> NetworkPlayVars:
        return self.vars


def handle_update_online_button(online_button: ttk.Button, is_logged_in: tk.BooleanVar) -> None:
    state = tk.NORMAL if is_logged_in.get() else tk.DISABLED
    online_button.configure(state=state)
