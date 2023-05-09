import typing

import tkinter as tk
import ttkbootstrap as ttk
from launcher.tk.page_frame import PageFrame
from launcher.tk.page_manager import PageManager
from launcher.pg.pg_launcher import PygameChessLauncher, Opponent


class OfflinePageButtons(typing.NamedTuple):
    vs_human: ttk.Button
    vs_bot: ttk.Button
    back: ttk.Button


class OfflinePage(PageFrame):
    def __init__(
            self,
            parent_frame: tk.Frame,
            page_manager: PageManager,
            pg_launcher: PygameChessLauncher
    ) -> None:
        super().__init__(parent_frame)
        buttons: OfflinePageButtons = self.create_buttons(page_manager, pg_launcher)
        label: ttk.Label = ttk.Label(self, text="Offline", font=("Verdana", 20))
        label.pack(expand=True)
        buttons.vs_human.pack(expand=True)
        buttons.vs_bot.pack(expand=True)
        buttons.back.pack(expand=True)

    def create_buttons(self, page_manager: PageManager, pg_launcher: PygameChessLauncher) -> OfflinePageButtons:
        vs_human_button: ttk.Button = ttk.Button(
            self, text="vs Human", command=lambda: pg_launcher.launch_single_player(Opponent.HUMAN))
        vs_bot_button: ttk.Button = ttk.Button(
            self, text="vs Bot", command=lambda: pg_launcher.launch_single_player(Opponent.BOT)
        )
        back_button: ttk.Button = ttk.Button(
            self, text="Back", command=lambda: page_manager.show_page("StartPage"))
        return OfflinePageButtons(vs_human_button, vs_bot_button, back_button)
