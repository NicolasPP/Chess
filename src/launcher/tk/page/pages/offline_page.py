import tkinter as tk
from ttkbootstrap import ttk
from launcher.tk.page.page_frame import PageFrame
from launcher.tk.page.page_manager import PageManager
from launcher.pg.pg_launcher import ChessPygameLauncher
from launcher.tk.components.offline_play_comp import OfflinePlayComponent
from launcher.tk.components.bot_config_comp import BotConfigComponent
from launcher.tk.components.time_config_comp import TimeConfigComponent
from launcher.tk.global_vars import GlobalUserVars
from config.tk_config import *


class OfflinePage(PageFrame):
    def __init__(self, parent_frame: ttk.Frame, page_manager: PageManager, pg_launcher: ChessPygameLauncher) -> None:
        super().__init__(parent_frame)

        back_button: ttk.Button = ttk.Button(self, text="back", command=lambda: page_manager.show_page("StartPage"))
        offline_play_comp: OfflinePlayComponent = OfflinePlayComponent(self, pg_launcher)
        bot_config_comp: BotConfigComponent = BotConfigComponent(self)
        time_config_comp: TimeConfigComponent = TimeConfigComponent(self)

        GlobalUserVars.get_is_bot_valid().trace_add(
            "write", lambda v, i, m: is_bot_valid_callback(offline_play_comp, bot_config_comp)
        )

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=8)
        self.grid_rowconfigure(1, weight=2)

        offline_play_comp.get_frame().grid(row=0, column=0, sticky=tk.NSEW, padx=OFFLINE_PAGE_PAD,
                                           pady=OFFLINE_PAGE_PAD)
        bot_config_comp.get_frame().grid(row=0, column=1, sticky=tk.NSEW, padx=OFFLINE_PAGE_PAD,
                                         pady=OFFLINE_PAGE_PAD, rowspan=2)
        time_config_comp.get_frame().grid(row=0, column=2, sticky=tk.NSEW, padx=OFFLINE_PAGE_PAD,
                                          pady=OFFLINE_PAGE_PAD, rowspan=2)
        back_button.grid(row=1, column=0, padx=OFFLINE_PAGE_PAD, pady=OFFLINE_PAGE_PAD)


def is_bot_valid_callback(offline_play_comp: OfflinePlayComponent, bot_config_comp: BotConfigComponent) -> None:
    offline_play_comp.is_bot_valid_callback()
    bot_config_comp.is_bot_valid_callback()
