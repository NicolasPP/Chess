import tkinter as tk

from ttkbootstrap import ttk

from config.tk_config import LAUNCHER_PAD
from launcher.tk.components.server_lobby_component import ServerLobbyComponent
from launcher.tk.global_vars import GlobalUserVars
from launcher.tk.launcher_user import LauncherUser
from launcher.tk.page.page_frame import PageFrame
from launcher.tk.page.page_manager import PageManager


class ServerPage(PageFrame):
    def __init__(
            self,
            parent_frame: tk.Frame,
            page_manager: PageManager,
    ) -> None:
        super().__init__(parent_frame)
        self.page_manager: PageManager = page_manager
        disconnect: ttk.Button = ttk.Button(self, text="Disconnect", command=self.handle_disconnect)
        GlobalUserVars.get().get_var(GlobalUserVars.server_disconnect).trace_add(
            "write", lambda v, i, m: self.server_disconnect_callback()
        )
        lobby_comp: ServerLobbyComponent = ServerLobbyComponent(self)

        self.grid_rowconfigure(0, weight=10)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=10)

        lobby_comp.get_frame().grid(row=0, column=0, padx=LAUNCHER_PAD, pady=LAUNCHER_PAD, sticky=tk.NSEW)
        disconnect.grid(row=1, column=0, padx=LAUNCHER_PAD, pady=LAUNCHER_PAD)

    def handle_disconnect(self) -> None:
        LauncherUser.get_client().disconnect()
        self.page_manager.show_page("OnlinePage")

    def server_disconnect_callback(self) -> None:
        if GlobalUserVars.get().get_var(GlobalUserVars.server_disconnect).get():
            self.page_manager.show_page("OnlinePage")
            GlobalUserVars.get().get_var(GlobalUserVars.server_disconnect).set(False)

    def handle_exit(self) -> None:
        pass
