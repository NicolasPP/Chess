import functools
import typing
import ttkbootstrap as ttk
from config.tk_config import *
from chess.bot.chess_bot_stockfish import StockFishBot
from launcher.tk.components.tk_component import Component
from config.user_config import UserConfig
from chess.asset.chess_assets import Themes


class SettingsWidgets(typing.NamedTuple):
    engine_valid: ttk.Label
    path_entry: ttk.Entry
    create_bot: ttk.Button
    theme_options: ttk.Menubutton
    theme_label: ttk.Label
    asset_options: ttk.Menubutton
    asset_label: ttk.Label
    size_scale: ttk.Scale
    size_scale_label: ttk.Label


class SettingsComponent(Component):

    def __init__(self, parent: ttk.Frame, is_bot_valid: ttk.BooleanVar) -> None:
        super().__init__(parent, "Settings")

        path_entry_str: ttk.StringVar = ttk.StringVar(value="stock fish engine path")
        settings_widgets = self.create_settings_widgets(path_entry_str)
        settings_widgets.create_bot[ttk.COMMAND] = lambda: create_bot_command(settings_widgets, is_bot_valid,
                                                                              path_entry_str)

        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_rowconfigure(2, weight=1)
        self.frame.grid_rowconfigure(3, weight=1)

        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)

        is_bot_valid.set(StockFishBot.create_bot())

        settings_widgets.size_scale_label.grid(row=0, column=0, sticky=ttk.EW, padx=SETTINGS_PAD, pady=SETTINGS_PAD)
        settings_widgets.size_scale.grid(row=0, column=1, sticky=ttk.NSEW, padx=SETTINGS_PAD, pady=SETTINGS_PAD)

        settings_widgets.theme_label.grid(row=1, column=0, sticky=ttk.NSEW, padx=SETTINGS_PAD, pady=SETTINGS_PAD)
        settings_widgets.theme_options.grid(row=1, column=1, sticky=ttk.NSEW, padx=SETTINGS_PAD, pady=SETTINGS_PAD)

        settings_widgets.asset_label.grid(row=2, column=0, sticky=ttk.NSEW, padx=SETTINGS_PAD, pady=SETTINGS_PAD)
        settings_widgets.asset_options.grid(row=2, column=1, sticky=ttk.NSEW, padx=SETTINGS_PAD, pady=SETTINGS_PAD)

        if is_bot_valid.get():
            settings_widgets.engine_valid.grid(row=3, column=0, columnspan=2, padx=SETTINGS_PAD, pady=SETTINGS_PAD)
        else:
            settings_widgets.path_entry.grid(row=3, column=0, sticky=ttk.NSEW, padx=SETTINGS_PAD, pady=SETTINGS_PAD)
            settings_widgets.create_bot.grid(row=3, column=1, sticky=ttk.NSEW, padx=SETTINGS_PAD, pady=SETTINGS_PAD)

    def create_settings_widgets(self, path_entry_str: ttk.StringVar) -> SettingsWidgets:
        engine_valid: ttk.Label = ttk.Label(self.frame, text="Stock Fish ready!", foreground='green')
        path_entry: ttk.Entry = ttk.Entry(self.frame, textvariable=path_entry_str, width=18)
        path_entry.bind("<Button>", lambda e: path_entry_str.set(''))
        create_bot: ttk.Button = ttk.Button(self.frame, text="create bot")

        theme_label: ttk.Label = ttk.Label(self.frame, text="Theme: ")
        theme_options: ttk.Menubutton = ttk.Menubutton(self.frame, text=Themes.get_name(UserConfig.get().data.theme_id),
                                                       width=SETTINGS_MENUBUTTON_WIDTH)
        theme_menu: ttk.Menu = ttk.Menu(theme_options)

        for theme_id in range(-1, 4):
            theme_menu.add_command(label=Themes.get_name(theme_id), background=BG_DARK, foreground=FG_DARK,
                                   command=functools.partial(handle_theme_selection, theme_id, theme_options))
        theme_options.configure(menu=theme_menu)

        asset_label: ttk.Label = ttk.Label(self.frame, text="Asset: ")
        asset_options: ttk.Menubutton = ttk.Menubutton(self.frame, text=UserConfig.get().data.asset_name,
                                                       width=SETTINGS_MENUBUTTON_WIDTH)
        asset_menu: ttk.Menu = ttk.Menu(asset_options)
        for option in ["SMALL", "LARGE", "RANDOM"]:
            asset_menu.add_command(label=option, background=BG_DARK, foreground=FG_DARK,
                                   command=functools.partial(handle_asset_selection, option, asset_options))
        asset_options.configure(menu=asset_menu)

        current_scale: float = UserConfig.get().data.scale
        size_scale_label: ttk.Label = ttk.Label(self.frame, text=f"size : {current_scale}", anchor=ttk.W,
                                                width=SCALE_LABEL_WIDTH)
        size_scale: ttk.Scale = ttk.Scale(self.frame, from_=3, to=7, style='warning', value=current_scale,
                                          command=lambda size: handle_scale_click(size, size_scale_label))
        return SettingsWidgets(engine_valid, path_entry, create_bot, theme_options, theme_label, asset_options,
                               asset_label, size_scale, size_scale_label)


def create_bot_command(settings_widgets: SettingsWidgets, is_bot_valid: ttk.BooleanVar,
                       path_entry_str: ttk.StringVar) -> None:
    if StockFishBot.create_bot(path_entry_str.get()):
        settings_widgets.create_bot.grid_forget()
        settings_widgets.path_entry.grid_forget()
        settings_widgets.engine_valid.grid(row=3, column=0, columnspan=2, padx=SETTINGS_PAD, pady=SETTINGS_PAD)
        is_bot_valid.set(True)
    else:
        path_entry_str.set("Path Incorrect")


def handle_scale_click(scale_size: str, size_scale_label: ttk.Label) -> None:
    size: float = float('%.2f' % float(scale_size))
    size_scale_label.configure(text=f"size: {size}")
    UserConfig.get().update_config(scale=size)


def handle_theme_selection(theme_id: int, menu_button: ttk.Menubutton) -> None:
    menu_button.configure(text=Themes.get_name(theme_id))
    UserConfig.get().update_config(theme_id=theme_id)


def handle_asset_selection(asset_name: str, menu_button: ttk.Menubutton) -> None:
    menu_button.configure(text=asset_name)
    UserConfig.get().update_config(asset_name=asset_name)
