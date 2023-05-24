import typing

import ttkbootstrap as ttk
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
                 is_bot_valid: ttk.BooleanVar) -> None:
        super().__init__(parent, "Play")
        buttons: OfflinePlayButtons = self.create_buttons(page_manager, pg_launcher)
        is_bot_valid.trace_add('write', lambda v, i, m: is_bot_valid_callback(is_bot_valid, buttons))

        self.is_bot_valid: ttk.BooleanVar = is_bot_valid
        set_bot_button_state(buttons, "normal" if is_bot_valid.get() else "disabled")

        buttons.vs_human.pack(expand=True)
        buttons.vs_bot.pack(expand=True)
        buttons.bot_vs_bot.pack(expand=True)
        buttons.back.pack(expand=True)

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


def is_bot_valid_callback(is_bot_valid: ttk.BooleanVar, offline_play_buttons: OfflinePlayButtons) -> None:
    state: str = ttk.NORMAL if is_bot_valid.get() else ttk.DISABLED
    set_bot_button_state(offline_play_buttons, state)


def set_bot_button_state(buttons: OfflinePlayButtons, state: str) -> None:
    buttons.vs_bot["state"] = state
    buttons.bot_vs_bot["state"] = state
