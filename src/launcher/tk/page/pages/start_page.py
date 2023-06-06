import tkinter as tk
from ttkbootstrap import ttk
from launcher.tk.page.page_frame import PageFrame
from launcher.tk.page.page_manager import PageManager
from config.tk_config import *
from database.chess_db import ChessDataBase
from launcher.tk.components.settings_comp import SettingsComponent
from launcher.tk.components.user_comp import UserComponent
from launcher.tk.components.network_play_comp import NetworkPlayComponent


class StartPage(PageFrame):

    def __init__(self, parent_frame: ttk.Frame, page_manager: PageManager, database: ChessDataBase) -> None:
        super().__init__(parent_frame)

        settings_comp: SettingsComponent = SettingsComponent(self)
        play_comp: NetworkPlayComponent = NetworkPlayComponent(self, page_manager)
        user_comp: UserComponent = UserComponent(self, database, play_comp.get_vars().is_logged_in)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        play_comp.get_frame().grid(row=0, column=0, sticky=tk.NSEW, padx=START_PAGE_FRAME_PAD,
                                   pady=START_PAGE_FRAME_PAD)
        settings_comp.get_frame().grid(row=0, column=1, rowspan=2, sticky=tk.NSEW, padx=START_PAGE_FRAME_PAD,
                                       pady=START_PAGE_FRAME_PAD)
        user_comp.get_frame().grid(row=1, column=0, sticky=tk.NSEW, padx=START_PAGE_FRAME_PAD,
                                   pady=START_PAGE_FRAME_PAD)
