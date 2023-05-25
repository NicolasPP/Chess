import tkinter as tk
from ttkbootstrap import ttk
from launcher.tk.page.page_frame import PageFrame
from launcher.tk.page.page_manager import PageManager
from launcher.pg.pg_launcher import ChessPygameLauncher
from launcher.tk.components.offline_play_comp import OfflinePlayComponent
from launcher.tk.components.bot_config_comp import BotConfigComponent
from launcher.tk.components.time_config_comp import TimeConfigComponent
from config.tk_config import *


class OfflinePage(PageFrame):
    def __init__(self, parent_frame: ttk.Frame, page_manager: PageManager, pg_launcher: ChessPygameLauncher,
                 is_bot_valid: tk.BooleanVar) -> None:
        super().__init__(parent_frame)

        offline_play_comp: OfflinePlayComponent = OfflinePlayComponent(self, page_manager, pg_launcher, is_bot_valid)
        bot_config_comp: BotConfigComponent = BotConfigComponent(self, is_bot_valid)
        time_config_comp: TimeConfigComponent = TimeConfigComponent(self)

        is_bot_valid.trace_add("write", lambda v, i, m: is_bot_valid_callback(offline_play_comp, bot_config_comp,
                                                                              is_bot_valid))

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        offline_play_comp.get_frame().grid(row=0, column=0, sticky=tk.NSEW, padx=OFFLINE_PAGE_PAD,
                                           pady=OFFLINE_PAGE_PAD)
        bot_config_comp.get_frame().grid(row=0, column=1, sticky=tk.NSEW, padx=OFFLINE_PAGE_PAD, pady=OFFLINE_PAGE_PAD)
        time_config_comp.get_frame().grid(row=0, column=2, sticky=tk.NSEW, padx=OFFLINE_PAGE_PAD,
                                          pady=OFFLINE_PAGE_PAD)


def is_bot_valid_callback(offline_play_comp: OfflinePlayComponent, bot_config_comp: BotConfigComponent, is_bot_valid:
                          tk.BooleanVar) -> None:
    offline_play_comp.is_bot_valid_callback(is_bot_valid)
    bot_config_comp.is_bot_valid_callback(is_bot_valid)
