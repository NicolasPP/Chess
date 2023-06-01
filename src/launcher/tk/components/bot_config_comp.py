import typing
from ttkbootstrap import ttk
import tkinter as tk
from launcher.tk.components.tk_component import Component
from config.user_config import UserConfig, PossibleConfigValues
from config.tk_config import *


class BotConfigCompWidgets(typing.NamedTuple):
    elo_scale: ttk.Scale
    elo_label: ttk.Label
    skill_scale: ttk.Scale
    skill_label: ttk.Label
    skill_value_label: ttk.Label
    elo_value_label: ttk.Label
    move_time_label: ttk.Label
    fast_move_button: ttk.Radiobutton
    regular_move_button: ttk.Radiobutton
    bot_side_label: ttk.Label
    white_side_button: ttk.Radiobutton
    black_side_button: ttk.Radiobutton


class BotConfigVars(typing.NamedTuple):
    elo_var: tk.StringVar
    skill_var: tk.StringVar
    time_var: tk.BooleanVar
    side_var: tk.StringVar


class BotConfigComponent(Component):

    @staticmethod
    def get_bot_vars() -> BotConfigVars:
        elo_var: tk.StringVar = tk.StringVar(value=UserConfig.get().data.bot_elo)
        skill_var: tk.StringVar = tk.StringVar(value=UserConfig.get().data.bot_skill_level)
        time_var: tk.BooleanVar = tk.BooleanVar(value=UserConfig.get().data.bot_use_time)
        side_var: tk.StringVar = tk.StringVar(value=UserConfig.get().data.bot_side_name)
        return BotConfigVars(elo_var, skill_var, time_var, side_var)

    def __init__(self, parent: ttk.Frame, is_bot_valid: tk.BooleanVar) -> None:
        if is_bot_valid.get():
            super().__init__(parent, "Bot Settings")
        else:
            super().__init__(parent, "Bot Unavailable")

        self.vars: BotConfigVars = BotConfigComponent.get_bot_vars()
        self.widgets: BotConfigCompWidgets = self.create_widgets(is_bot_valid)

        self.vars.time_var.trace_add("write", lambda v, i, m: self.time_var_callback())
        self.vars.side_var.trace_add("write", lambda v, i, m: self.side_var_callback())

        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_rowconfigure(2, weight=1)
        self.frame.grid_rowconfigure(3, weight=1)

        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)
        self.frame.grid_columnconfigure(2, weight=1)

        self.widgets.elo_label.grid(row=0, column=0, sticky=tk.NSEW, pady=BOT_CONFIG_PAD, padx=BOT_CONFIG_PAD)
        self.widgets.elo_scale.grid(row=0, column=1, sticky=tk.NSEW, pady=BOT_CONFIG_PAD, padx=BOT_CONFIG_PAD)
        self.widgets.elo_value_label.grid(row=0, column=2, pady=BOT_CONFIG_PAD, padx=BOT_CONFIG_PAD)

        self.widgets.skill_label.grid(row=1, column=0, sticky=tk.NSEW, pady=BOT_CONFIG_PAD, padx=BOT_CONFIG_PAD)
        self.widgets.skill_scale.grid(row=1, column=1, sticky=tk.NSEW, pady=BOT_CONFIG_PAD, padx=BOT_CONFIG_PAD)
        self.widgets.skill_value_label.grid(row=1, column=2, pady=BOT_CONFIG_PAD, padx=BOT_CONFIG_PAD)

        self.widgets.move_time_label.grid(row=2, column=0, sticky=tk.NSEW, pady=BOT_CONFIG_PAD,
                                          padx=(BOT_CONFIG_PAD, 0))
        self.widgets.regular_move_button.grid(row=2, column=1, sticky=tk.NSEW, pady=BOT_CONFIG_PAD, padx=BOT_CONFIG_PAD)
        self.widgets.fast_move_button.grid(row=2, column=2, sticky=tk.NSEW, pady=BOT_CONFIG_PAD, padx=BOT_CONFIG_PAD)

        self.widgets.bot_side_label.grid(row=3, column=0, sticky=tk.NSEW, pady=BOT_CONFIG_PAD, padx=(BOT_CONFIG_PAD, 0))
        self.widgets.white_side_button.grid(row=3, column=1, sticky=tk.NSEW, pady=BOT_CONFIG_PAD, padx=BOT_CONFIG_PAD)
        self.widgets.black_side_button.grid(row=3, column=2, sticky=tk.NSEW, pady=BOT_CONFIG_PAD, padx=BOT_CONFIG_PAD)

    def create_widgets(self, is_bot_valid: tk.BooleanVar) -> BotConfigCompWidgets:
        state = tk.DISABLED if not is_bot_valid.get() else tk.NORMAL
        elo_scale: ttk.Scale = ttk.Scale(self.frame, from_=MIN_ELO, to=MAX_ELO, value=UserConfig.get().data.bot_elo,
                                         command=lambda size: handle_scale_click(self.vars, bot_elo=int(float(size))),
                                         state=state, style="warning")
        elo_label: ttk.Label = ttk.Label(self.frame, text="bot elo: ", state=state)

        skill_scale: ttk.Scale = ttk.Scale(self.frame, from_=MIN_SKILL, to=MAX_SKILL,
                                           value=UserConfig.get().data.bot_skill_level, state=state, style="warning",
                                           command=lambda size: handle_scale_click(self.vars,
                                                                                   bot_skill_level=int(float(size))))
        skill_label: ttk.Label = ttk.Label(self.frame, text="bot skill: ", state=state)
        skill_value_label: ttk.Label = ttk.Label(self.frame, textvariable=self.vars.skill_var, state=state)
        elo_value_label: ttk.Label = ttk.Label(self.frame, textvariable=self.vars.elo_var, state=state)
        move_time_label: ttk.Label = ttk.Label(self.frame, text="move time: ", state=state)
        fast_move_button: ttk.Radiobutton = ttk.Radiobutton(self.frame, text="fast", variable=self.vars.time_var,
                                                            value=False, style="toolbutton", state=state)
        regular_move_button: ttk.Radiobutton = ttk.Radiobutton(self.frame, text="regular", style="toolbutton",
                                                               variable=self.vars.time_var, value=True, state=state)
        bot_side_label: ttk.Label = ttk.Label(self.frame, text="bot side: ", state=state)
        white_side_button: ttk.Radiobutton = ttk.Radiobutton(self.frame, text="white", variable=self.vars.side_var,
                                                             value="WHITE", style="toolbutton", state=state)
        black_side_button: ttk.Radiobutton = ttk.Radiobutton(self.frame, text="black", variable=self.vars.side_var,
                                                             value="BLACK", style="toolbutton", state=state)
        return BotConfigCompWidgets(elo_scale, elo_label, skill_scale, skill_label, skill_value_label, elo_value_label,
                                    move_time_label, fast_move_button, regular_move_button, bot_side_label,
                                    white_side_button, black_side_button)

    def is_bot_valid_callback(self, is_bot_valid: tk.BooleanVar) -> None:
        state = tk.DISABLED if not is_bot_valid.get() else tk.NORMAL
        if is_bot_valid.get():
            self.set_title("Bot Settings")

        for widget in self.get_widget_list():
            widget.configure(state=state)

    def get_widget_list(self) -> list[ttk.Scale | ttk.Button | ttk.Label]:
        return [self.widgets.elo_scale, self.widgets.elo_label, self.widgets.skill_scale, self.widgets.skill_label,
                self.widgets.skill_value_label, self.widgets.elo_value_label, self.widgets.move_time_label,
                self.widgets.fast_move_button, self.widgets.regular_move_button, self.widgets.bot_side_label,
                self.widgets.white_side_button, self.widgets.black_side_button]

    def time_var_callback(self) -> None:
        UserConfig.get().update_config(bot_use_time=self.vars.time_var.get())

    def side_var_callback(self) -> None:
        UserConfig.get().update_config(bot_side_name=self.vars.side_var.get())


def handle_scale_click(bot_vars: BotConfigVars, **args: PossibleConfigValues) -> None:
    elo_value: int | None = args.get("bot_elo")
    skill_value: int | None = args.get("bot_skill_level")

    if elo_value is not None: bot_vars.elo_var.set(str(elo_value))
    if skill_value is not None: bot_vars.skill_var.set(str(skill_value))

    UserConfig.get().update_config(**args)
