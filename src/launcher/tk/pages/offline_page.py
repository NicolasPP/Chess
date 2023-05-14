import typing

import tkinter as tk
import ttkbootstrap as ttk
from launcher.tk.page_frame import PageFrame
from launcher.tk.page_manager import PageManager
from launcher.pg.pg_launcher import PygameChessLauncher, SinglePlayerGameType
from config.tk_config import *


class OfflinePageButtons(typing.NamedTuple):
    vs_human: ttk.Button
    vs_bot: ttk.Button
    bot_vs_bot: ttk.Button
    back: ttk.Button


class OfflinePage(PageFrame):
    def __init__(self, parent_frame: tk.Frame, page_manager: PageManager, pg_launcher: PygameChessLauncher,
                 is_bot_valid: ttk.BooleanVar) -> None:
        super().__init__(parent_frame)
        self.buttons: OfflinePageButtons = self.create_buttons(page_manager, pg_launcher)
        label: ttk.Label = ttk.Label(self, text="Offline", font=(FONT_NAME, 20), style='title.TLabel')

        self.is_bot_valid: ttk.BooleanVar = is_bot_valid
        self.set_bot_button_state("disabled")

        is_bot_valid.trace_add('write', self.is_bot_valid_callback)

        label.pack(expand=True)
        self.buttons.vs_human.pack(expand=True)
        self.buttons.vs_bot.pack(expand=True)
        self.buttons.bot_vs_bot.pack(expand=True)
        self.buttons.back.pack(expand=True)

    def set_bot_button_state(self, state: str) -> None:
        self.buttons.vs_bot["state"] = state
        self.buttons.bot_vs_bot["state"] = state

    def create_buttons(self, page_manager: PageManager, pg_launcher: PygameChessLauncher) -> OfflinePageButtons:
        human_button: ttk.Button = ttk.Button(self, text="vs Human", command=lambda: pg_launcher.launch_single_player(
            SinglePlayerGameType.HUMAN_VS_HUMAN))
        bot_button: ttk.Button = ttk.Button(self, text="vs Bot", command=lambda: pg_launcher.launch_single_player(
            SinglePlayerGameType.HUMAN_VS_BOT))
        bot_vs_bot: ttk.Button = ttk.Button(self, text="bot vs bot", command=lambda: pg_launcher.launch_single_player(
            SinglePlayerGameType.BOT_VS_BOT))
        back_button: ttk.Button = ttk.Button(self, text="Back", command=lambda: page_manager.show_page("StartPage"))
        return OfflinePageButtons(human_button, bot_button, bot_vs_bot, back_button)

    def is_bot_valid_callback(self, var: str, index: str, mode: str) -> None:
        state: str = "normal" if self.is_bot_valid.get() else "disabled"
        self.set_bot_button_state(state)
