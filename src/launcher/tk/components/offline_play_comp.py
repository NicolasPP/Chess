import tkinter as tk
import typing

from ttkbootstrap import ttk

from launcher.pg.pg_launcher import ChessPygameLauncher
from launcher.pg.pg_launcher import SinglePlayerGameType
from launcher.tk.components.tk_component import Component
from launcher.tk.global_vars import GlobalUserVars


class OfflinePlayButtons(typing.NamedTuple):
    vs_human: ttk.Button
    vs_bot: ttk.Button
    bot_vs_bot: ttk.Button


class OfflinePlayComponent(Component):
    def __init__(self, parent: ttk.Frame) -> None:
        super().__init__(parent, "Play")
        self.buttons: OfflinePlayButtons = self.create_buttons()

        self.set_bot_button_state(tk.NORMAL if GlobalUserVars.get().get_var(GlobalUserVars.is_bot_valid).get() else
                                  tk.DISABLED)

        self.buttons.vs_human.pack(expand=True)
        self.buttons.vs_bot.pack(expand=True)
        self.buttons.bot_vs_bot.pack(expand=True)

    def create_buttons(self) -> OfflinePlayButtons:
        pg_launcher: ChessPygameLauncher = ChessPygameLauncher.get()
        human_button: ttk.Button = ttk.Button(self.frame, text="vs Human", command=lambda:
                                              pg_launcher.launch_single_player(SinglePlayerGameType.HUMAN_VS_HUMAN))
        bot_button: ttk.Button = ttk.Button(self.frame, text="vs Bot", command=lambda: pg_launcher.launch_single_player(
                                            SinglePlayerGameType.HUMAN_VS_BOT))
        bot_vs_bot: ttk.Button = ttk.Button(self.frame, text="bot vs bot", command=lambda:
                                            pg_launcher.launch_single_player(SinglePlayerGameType.BOT_VS_BOT))
        return OfflinePlayButtons(human_button, bot_button, bot_vs_bot)

    def is_bot_valid_callback(self) -> None:
        state: str = tk.NORMAL if GlobalUserVars.get().get_var(GlobalUserVars.is_bot_valid).get() else tk.DISABLED
        self.set_bot_button_state(state)

    def set_bot_button_state(self, state: str) -> None:
        self.buttons.vs_bot.configure(state=state)
        self.buttons.bot_vs_bot.configure(state=state)
