import typing

import tkinter as tk
import ttkbootstrap as ttk
from launcher.tk.page_frame import PageFrame
from launcher.tk.page_manager import PageManager
from launcher.pg.pg_launcher import PygameChessLauncher
from config.tk_config import *


class OnlinePageButtons(typing.NamedTuple):
    back: ttk.Button


class OnlinePage(PageFrame):
    def __init__(self, parent_frame: tk.Frame, page_manager: PageManager, pg_launcher: PygameChessLauncher) -> None:
        super().__init__(parent_frame)
        buttons: OnlinePageButtons = self.create_buttons(page_manager)
        label: ttk.Label = ttk.Label(self, text="Online", font=(FONT_NAME, 20), style="title.TLabel")
        label.pack()
        buttons.back.pack()

    def create_buttons(self, page_manager: PageManager) -> OnlinePageButtons:
        back_button: ttk.Button = ttk.Button(self, text="Back", command=lambda: page_manager.show_page("StartPage"))
        return OnlinePageButtons(back_button)
