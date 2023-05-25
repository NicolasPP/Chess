import typing
import tkinter as tk
from ttkbootstrap import ttk
from launcher.tk.page.page_manager import PageManager
from launcher.pg.pg_launcher import ChessPygameLauncher, SinglePlayerGameType
from launcher.tk.components.tk_component import Component


class OfflinePlayButtons(typing.NamedTuple):
    vs_human: ttk.Button
    vs_bot: ttk.Button
    bot_vs_bot: ttk.Button
    back: ttk.Button


class OfflinePlayComponent(Component):
    def __init__(self, parent: ttk.Frame, page_manager: PageManager, pg_launcher: ChessPygameLauncher,
                 is_bot_valid: tk.BooleanVar) -> None:
        super().__init__(parent, "Play")
        self.buttons: OfflinePlayButtons = self.create_buttons(page_manager, pg_launcher)

        self.is_bot_valid: tk.BooleanVar = is_bot_valid
        self.set_bot_button_state("normal" if is_bot_valid.get() else "disabled")

        self.buttons.vs_human.pack(expand=True)
        self.buttons.vs_bot.pack(expand=True)
        self.buttons.bot_vs_bot.pack(expand=True)
        self.buttons.back.pack(expand=True)

    def create_buttons(self, page_manager: PageManager, pg_launcher: ChessPygameLauncher) -> OfflinePlayButtons:
        human_button: ttk.Button = ttk.Button(self.frame, text="vs Human", command=lambda:
                                              pg_launcher.launch_single_player(SinglePlayerGameType.HUMAN_VS_HUMAN))
        bot_button: ttk.Button = ttk.Button(self.frame, text="vs Bot", command=lambda: pg_launcher.launch_single_player(
                                            SinglePlayerGameType.HUMAN_VS_BOT))
        bot_vs_bot: ttk.Button = ttk.Button(self.frame, text="bot vs bot", command=lambda:
                                            pg_launcher.launch_single_player(SinglePlayerGameType.BOT_VS_BOT))
        back_button: ttk.Button = ttk.Button(self.frame, text="Back", command=lambda: page_manager.show_page(
                                             "StartPage"))
        return OfflinePlayButtons(human_button, bot_button, bot_vs_bot, back_button)

    def is_bot_valid_callback(self, is_bot_valid: tk.BooleanVar) -> None:
        state: str = tk.NORMAL if is_bot_valid.get() else tk.DISABLED
        self.set_bot_button_state(state)

    def set_bot_button_state(self, state: str) -> None:
        self.buttons.vs_bot["state"] = state
        self.buttons.bot_vs_bot["state"] = state
