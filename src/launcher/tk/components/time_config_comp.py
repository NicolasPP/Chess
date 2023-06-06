import functools
import tkinter as tk
import typing

from ttkbootstrap import ttk

from chess.timer.timer_config import DefaultConfigs
from chess.timer.timer_config import TimerConfig
from config.tk_config import BG_DARK
from config.tk_config import DEFAULT_TIME_PAD
from config.tk_config import FG_DARK
from config.tk_config import TIME_ENTRY_PAD
from config.tk_config import TIME_ENTRY_WIDTH
from config.user_config import UserConfig
from launcher.tk.components.tk_component import Component


class TimeConfigWidgets(typing.NamedTuple):
    time_entry: ttk.Entry
    increment_entry: ttk.Entry
    time_label: ttk.Label
    increment_label: ttk.Label
    default_time_label: ttk.Label
    bullet_times: ttk.Menubutton
    blitz_times: ttk.Menubutton
    rapid_times: ttk.Menubutton


class TimeConfigVars(typing.NamedTuple):
    time_var: tk.StringVar
    increment_var: tk.StringVar
    current_time_var: tk.StringVar


class TimeConfigComponent(Component):

    def __init__(self, parent: ttk.Frame) -> None:
        super().__init__(parent, "Time Config")

        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)
        self.frame.grid_columnconfigure(2, weight=1)
        self.frame.grid_columnconfigure(3, weight=1)

        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_rowconfigure(2, weight=1)
        self.frame.grid_rowconfigure(3, weight=1)
        self.frame.grid_rowconfigure(4, weight=1)

        self.vars: TimeConfigVars = self.create_vars()
        self.widgets: TimeConfigWidgets = self.create_widgets()

        self.widgets.time_label.grid(row=0, column=0, pady=TIME_ENTRY_PAD)
        self.widgets.time_entry.grid(row=0, column=1, pady=TIME_ENTRY_PAD)
        self.widgets.increment_label.grid(row=0, column=2, pady=TIME_ENTRY_PAD)
        self.widgets.increment_entry.grid(row=0, column=3, pady=TIME_ENTRY_PAD)

        self.widgets.default_time_label.grid(row=1, column=0, columnspan=4, pady=DEFAULT_TIME_PAD)
        self.widgets.bullet_times.grid(row=2, column=0, columnspan=4, pady=DEFAULT_TIME_PAD)
        self.widgets.blitz_times.grid(row=3, column=0, columnspan=4, pady=DEFAULT_TIME_PAD)
        self.widgets.rapid_times.grid(row=4, column=0, columnspan=4, pady=DEFAULT_TIME_PAD)

    def create_widgets(self) -> TimeConfigWidgets:
        time_entry: ttk.Entry = ttk.Entry(self.frame, textvariable=self.vars.time_var, width=TIME_ENTRY_WIDTH)
        time_entry.bind("<Button>", lambda e: self.vars.time_var.set(''))
        increment_entry: ttk.Entry = ttk.Entry(self.frame, textvariable=self.vars.increment_var, width=TIME_ENTRY_WIDTH)
        increment_entry.bind("<Button>", lambda e: self.vars.increment_var.set(''))
        time_label: ttk.Label = ttk.Label(self.frame, text="Time")
        increment_label: ttk.Label = ttk.Label(self.frame, text="Incr")
        default_time_label: ttk.Label = ttk.Label(self.frame, text="Default Times", anchor=tk.CENTER)

        def add_menu_command(menu: tk.Menu, *timer_configs: TimerConfig) -> None:
            for timer_config in timer_configs:
                menu.add_command(label=timer_config.get_name(), background=BG_DARK, foreground=FG_DARK,
                                 command=functools.partial(self.handle_time_click, timer_config))

        bullet_times: ttk.Menubutton = ttk.Menubutton(self.frame, text="Bullet times")
        bullet_times_menu: tk.Menu = tk.Menu(bullet_times)
        add_menu_command(bullet_times_menu, DefaultConfigs.BULLET_1_0, DefaultConfigs.BULLET_1_1,
                         DefaultConfigs.BULLET_2_1)
        bullet_times.configure(menu=bullet_times_menu)

        blitz_times: ttk.Menubutton = ttk.Menubutton(self.frame, text="Blitz times")
        blitz_times_menu: tk.Menu = tk.Menu(blitz_times)
        add_menu_command(blitz_times_menu, DefaultConfigs.BLITZ_3_0, DefaultConfigs.BLITZ_3_2,
                         DefaultConfigs.BLITZ_5_0)
        blitz_times.configure(menu=blitz_times_menu)

        rapid_times: ttk.Menubutton = ttk.Menubutton(self.frame, text="Rapid times")
        rapid_times_menu: tk.Menu = tk.Menu(rapid_times)
        add_menu_command(rapid_times_menu, DefaultConfigs.RAPID_15_10, DefaultConfigs.RAPID_30_0,
                         DefaultConfigs.RAPID_60_0)
        rapid_times.configure(menu=rapid_times_menu)

        return TimeConfigWidgets(time_entry, increment_entry, time_label, increment_label, default_time_label,
                                 bullet_times, blitz_times, rapid_times)

    def handle_entry_var(self) -> None:
        if len(self.vars.time_var.get()) == 0:
            self.vars.time_var.set('mins')

        if len(self.vars.increment_var.get()) == 0:
            self.vars.increment_var.set('secs')

        if not self.vars.increment_var.get().isnumeric() or \
            not self.vars.time_var.get().isnumeric(): return

        time: int = int(self.vars.time_var.get())
        increment: int = int(self.vars.increment_var.get())
        UserConfig.get().update_config(timer_config_name=f"{time} {increment}")

    def create_vars(self) -> TimeConfigVars:
        time_var: tk.StringVar = tk.StringVar(value="mins")
        time_var.trace_add("write", lambda v, i, m: self.handle_entry_var())
        increment_var: tk.StringVar = tk.StringVar(value="secs")
        increment_var.trace_add("write", lambda v, i, m: self.handle_entry_var())
        current_time_var: tk.StringVar = tk.StringVar(value=TimerConfig.get_timer_config(UserConfig.get(
                                                      ).data.timer_config_name).get_value_str())
        return TimeConfigVars(time_var, increment_var, current_time_var)

    def handle_time_click(self, time_config: TimerConfig) -> None:
        self.vars.time_var.set(str(time_config.time // 60))
        self.vars.increment_var.set(str(time_config.increment))
        UserConfig.get().update_config(timer_config_name=time_config.get_name())
