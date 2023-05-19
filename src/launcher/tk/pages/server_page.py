import tkinter as tk
from launcher.tk.page_frame import PageFrame
from launcher.tk.page_manager import PageManager
from launcher.pg.pg_launcher import ChessPygameLauncher


class ServerPage(PageFrame):
    def __init__(
            self,
            parent_frame: tk.Frame,
            page_manager: PageManager,
            pg_launcher: ChessPygameLauncher
    ) -> None:
        super().__init__(parent_frame)
