import tkinter as tk
from ttkbootstrap import ttk
from launcher.tk.page.page_frame import PageFrame
from launcher.tk.page.page_manager import PageManager
from launcher.pg.pg_launcher import ChessPygameLauncher
from launcher.tk.components.chat_component import ChatComponent
from launcher.tk.components.server_lobby_component import ServerLobbyComponent
from launcher.tk.launcher_user import LauncherUser
from launcher.tk.global_vars import GlobalUserVars
from config.tk_config import *


class ServerPage(PageFrame):
    def __init__(
            self,
            parent_frame: tk.Frame,
            page_manager: PageManager,
            pg_launcher: ChessPygameLauncher
    ) -> None:
        super().__init__(parent_frame)
        self.page_manager: PageManager = page_manager
        disconnect: ttk.Button = ttk.Button(self, text="Disconnect", command=self.handle_disconnect)
        GlobalUserVars.get_server_disconnect().trace_add("write", lambda v, i, m: self.server_disconnect_callback())
        chat_comp: ChatComponent = ChatComponent(self)
        lobby_comp: ServerLobbyComponent = ServerLobbyComponent(self)

        self.grid_rowconfigure(0, weight=10)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=6)
        self.grid_columnconfigure(1, weight=2)

        lobby_comp.get_frame().grid(row=0, column=0, rowspan=2, padx=SERVER_PAD, pady=SERVER_PAD, sticky=tk.NSEW)
        chat_comp.get_frame().grid(row=0, column=1, padx=SERVER_PAD, pady=SERVER_PAD, sticky=tk.NSEW)
        disconnect.grid(row=1, column=1)

    def handle_disconnect(self) -> None:
        LauncherUser.get_client().disconnect()
        self.page_manager.show_page("OnlinePage")

    def server_disconnect_callback(self) -> None:
        if GlobalUserVars.get_server_disconnect().get():
            self.page_manager.show_page("OnlinePage")
            GlobalUserVars.get_server_disconnect().set(False)
