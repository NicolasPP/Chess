import tkinter as tk
import ttkbootstrap as ttk
from launcher.tk.page.page_frame import PageFrame
from launcher.tk.page.page_manager import PageManager
from launcher.pg.pg_launcher import ChessPygameLauncher
from launcher.tk.components.offline_play_comp import OfflinePlayComponent
from launcher.tk.components.bot_config_comp import BotConfigComponent
from launcher.tk.components.time_config_comp import TimeConfigComponent
from config.tk_config import *


class OfflinePage(PageFrame):
    def __init__(self, parent_frame: tk.Frame, page_manager: PageManager, pg_launcher: ChessPygameLauncher,
                 is_bot_valid: ttk.BooleanVar) -> None:
        super().__init__(parent_frame)
        offline_play_comp: OfflinePlayComponent = OfflinePlayComponent(self, page_manager, pg_launcher, is_bot_valid)
        bot_config_comp: BotConfigComponent = BotConfigComponent(self)
        time_config_comp: TimeConfigComponent = TimeConfigComponent(self)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        offline_play_comp.get_frame().grid(row=0, column=0, sticky=ttk.NSEW, padx=OFFLINE_PAGE_PAD,
                                           pady=OFFLINE_PAGE_PAD)
        bot_config_comp.get_frame().grid(row=0, column=1, sticky=ttk.NSEW, padx=OFFLINE_PAGE_PAD, pady=OFFLINE_PAGE_PAD)
        time_config_comp.get_frame().grid(row=0, column=2, sticky=ttk.NSEW, padx=OFFLINE_PAGE_PAD,
                                          pady=OFFLINE_PAGE_PAD)
