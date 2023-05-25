import typing
from ttkbootstrap import ttk
import tkinter as tk
from launcher.tk.components.tk_component import Component
from config.user_config import UserConfig
from config.tk_config import *


class BotConfigCompWidgets(typing.NamedTuple):
    elo_scale: ttk.Scale
    elo_label: ttk.Label
    skill_scale: ttk.Scale
    skill_label: ttk.Label


class BotConfigComponent(Component):
    def __init__(self, parent: ttk.Frame, is_bot_valid: tk.BooleanVar) -> None:
        super().__init__(parent, "Bot Settings")
        self.widgets: BotConfigCompWidgets = self.create_widgets(is_bot_valid)

        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)

        self.widgets.elo_label.grid(row=0, column=0, sticky=tk.NSEW, pady=BOT_CONFIG_PAD, padx=BOT_CONFIG_PAD)
        self.widgets.elo_scale.grid(row=0, column=1, sticky=tk.NSEW, pady=BOT_CONFIG_PAD, padx=BOT_CONFIG_PAD)
        self.widgets.skill_label.grid(row=1, column=0, sticky=tk.NSEW, pady=BOT_CONFIG_PAD, padx=BOT_CONFIG_PAD)
        self.widgets.skill_scale.grid(row=1, column=1, sticky=tk.NSEW, pady=BOT_CONFIG_PAD, padx=BOT_CONFIG_PAD)

    def create_widgets(self, is_bot_valid: tk.BooleanVar) -> BotConfigCompWidgets:
        state = tk.DISABLED if not is_bot_valid.get() else tk.NORMAL
        elo_scale: ttk.Scale = ttk.Scale(self.frame, from_=MIN_ELO, to=MAX_ELO, value=UserConfig.get().data.bot_elo,
                                         command=lambda size: UserConfig.get().update_config(bot_elo=int(float(size))),
                                         state=state, style="WARNING")
        elo_label: ttk.Label = ttk.Label(self.frame, text="bot elo: ")

        skill_scale: ttk.Scale = ttk.Scale(self.frame, from_=MIN_SKILL, to=MAX_SKILL,
                                           value=UserConfig.get().data.bot_skill_level,
                                           command=lambda size: UserConfig.get().update_config(
                                                bot_skill_level=int(float(size))), state=state, style="warning")
        skill_label: ttk.Label = ttk.Label(self.frame, text="bot skill: ")
        return BotConfigCompWidgets(elo_scale, elo_label, skill_scale, skill_label)

    def is_bot_valid_callback(self, is_bot_valid: tk.BooleanVar) -> None:
        state = tk.DISABLED if not is_bot_valid.get() else tk.NORMAL
        self.widgets.elo_scale["state"] = state
        self.widgets.skill_scale["state"] = state
