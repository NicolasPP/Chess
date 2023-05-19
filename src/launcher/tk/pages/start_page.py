import typing
import tkinter as tk
import ttkbootstrap as ttk
from launcher.tk.page_frame import PageFrame
from launcher.tk.page_manager import PageManager
from config.tk_config import *
from chess.bot.chess_bot_stockfish import StockFishBot
from launcher.pg.pg_launcher import PossibleConfigValues, ChessPygameLauncher


class PlayButtons(typing.NamedTuple):
    online: ttk.Button
    offline: ttk.Button


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


class StartPage(PageFrame):

    @staticmethod
    def create_play_buttons(page_manger: PageManager, play_frame: ttk.LabelFrame) -> PlayButtons:
        online_button: ttk.Button = ttk.Button(play_frame, text="Online",
                                               command=lambda: page_manger.show_page("OnlinePage"))
        offline_button: ttk.Button = ttk.Button(play_frame, text="Offline",
                                                command=lambda: page_manger.show_page("OfflinePage"))
        return PlayButtons(online_button, offline_button)

    @staticmethod
    def create_settings_widgets(settings_frame: ttk.LabelFrame, path_entry_str: ttk.StringVar,
                                pg_launcher: ChessPygameLauncher) -> SettingsWidgets:
        engine_valid: ttk.Label = ttk.Label(settings_frame, text="Stock Fish ready!", foreground='green')
        path_entry: ttk.Entry = ttk.Entry(settings_frame, textvariable=path_entry_str, width=18)
        path_entry.bind("<Button>", lambda e: path_entry_str.set(''))
        create_bot: ttk.Button = ttk.Button(settings_frame, text="create bot")

        theme_label: ttk.Label = ttk.Label(settings_frame, text="Theme: ")
        theme_id_name: str = str(pg_launcher.config.data.theme_id)
        if theme_id_name == "-1": theme_id_name = 'RANDOM'
        theme_options: ttk.Menubutton = ttk.Menubutton(settings_frame, text=theme_id_name)
        theme_menu: ttk.Menu = ttk.Menu(theme_options)
        theme_menu.add_radiobutton(value="1", label="1", background=BG_DARK, foreground=FG_DARK,
                                   command=lambda: configure_pygame_launcher(pg_launcher, theme_options, theme_id=1))
        theme_menu.add_radiobutton(value="2", label="2", background=BG_DARK, foreground=FG_DARK,
                                   command=lambda: configure_pygame_launcher(pg_launcher, theme_options, theme_id=2))
        theme_menu.add_radiobutton(value="3", label="3", background=BG_DARK, foreground=FG_DARK,
                                   command=lambda: configure_pygame_launcher(pg_launcher, theme_options, theme_id=3))
        theme_menu.add_radiobutton(value="4", label="4", background=BG_DARK, foreground=FG_DARK,
                                   command=lambda: configure_pygame_launcher(pg_launcher, theme_options, theme_id=4))
        theme_menu.add_radiobutton(value="RANDOM", label="RANDOM", background=BG_DARK, foreground=FG_DARK,
                                   command=lambda: configure_pygame_launcher(pg_launcher, theme_options, theme_id=-1))
        theme_options['menu'] = theme_menu

        asset_label: ttk.Label = ttk.Label(settings_frame, text="Asset: ")
        asset_options: ttk.Menubutton = ttk.Menubutton(settings_frame, text=pg_launcher.config.data.asset_name)
        asset_menu: ttk.Menu = ttk.Menu(asset_options)
        asset_menu.add_radiobutton(value="SMALL", label="SMALL", background=BG_DARK, foreground=FG_DARK,
                                   command=lambda: configure_pygame_launcher(pg_launcher, asset_options,
                                                                             asset_name="SMALL"))
        asset_menu.add_radiobutton(value="LARGE", label="LARGE", background=BG_DARK, foreground=FG_DARK,
                                   command=lambda: configure_pygame_launcher(pg_launcher, asset_options,
                                                                             asset_name="LARGE"))
        asset_options['menu'] = asset_menu
        current_scale: float = pg_launcher.config.data.scale
        size_scale_label: ttk.Label = ttk.Label(settings_frame, text=f"game size : {current_scale}", width=13,
                                                anchor='w')
        size_scale: ttk.Scale = ttk.Scale(settings_frame, from_=3, to=7, style='warning', value=current_scale,
                                          command=lambda size: handle_scale_click(size, size_scale_label, pg_launcher))
        return SettingsWidgets(engine_valid, path_entry, create_bot, theme_options, theme_label, asset_options,
                               asset_label, size_scale, size_scale_label)

    def __init__(self, parent_frame: tk.Frame, page_manager: PageManager, is_bot_valid: ttk.BooleanVar,
                 pg_launcher: ChessPygameLauncher) -> None:
        super().__init__(parent_frame)
        play_frame: ttk.LabelFrame = ttk.LabelFrame(self, text='Play')
        settings_frame: ttk.LabelFrame = ttk.LabelFrame(self, text='Settings')
        user_frame: ttk.LabelFrame = ttk.LabelFrame(self, text='User')

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=5)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=10)

        play_buttons = StartPage.create_play_buttons(page_manager, play_frame)
        play_frame.grid(row=0, column=0, sticky=ttk.NSEW, padx=START_PAGE_FRAME_PAD, pady=START_PAGE_FRAME_PAD)
        play_buttons.online.pack(side=ttk.LEFT, expand=True, anchor=ttk.CENTER)
        play_buttons.offline.pack(side=ttk.LEFT, expand=True, anchor=ttk.CENTER)

        path_entry_str: ttk.StringVar = ttk.StringVar(value="stock fish engine path")
        settings_widgets = StartPage.create_settings_widgets(settings_frame, path_entry_str, pg_launcher)

        settings_frame.grid(row=0, column=1, rowspan=2, sticky=ttk.NSEW, padx=START_PAGE_FRAME_PAD,
                            pady=START_PAGE_FRAME_PAD)
        settings_widgets.create_bot["command"] = lambda: create_bot_command(settings_widgets, is_bot_valid,
                                                                            path_entry_str)

        is_bot_valid.set(StockFishBot.create_bot())

        settings_frame.grid_columnconfigure(0, weight=1)
        settings_frame.grid_columnconfigure(1, weight=1)

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

        user_frame.grid(row=1, column=0, sticky=ttk.NSEW, padx=START_PAGE_FRAME_PAD, pady=START_PAGE_FRAME_PAD)


def create_bot_command(settings_widgets: SettingsWidgets, is_bot_valid: ttk.BooleanVar,
                       path_entry_str: ttk.StringVar) -> None:
    if StockFishBot.create_bot(path_entry_str.get()):
        settings_widgets.create_bot.grid_forget()
        settings_widgets.path_entry.grid_forget()
        settings_widgets.engine_valid.grid(row=3, column=0, columnspan=2, padx=SETTINGS_PAD, pady=SETTINGS_PAD)
        is_bot_valid.set(True)
    else:
        path_entry_str.set("Path Incorrect")


def configure_pygame_launcher(pygame_launcher: ChessPygameLauncher, menu_button: ttk.Menubutton,
                              **args: PossibleConfigValues) -> None:
    assert len(args) == 1, 'invalid number of args'
    for value in args.values():
        if value == -1: value = 'RANDOM'
        menu_button['text'] = value
    pygame_launcher.update_config(**args)


def handle_scale_click(scale_size: str, size_scale_label: ttk.Label, pygame_launcher: ChessPygameLauncher) -> None:
    size: float = float('%.2f' % float(scale_size))
    size_scale_label["text"] = f"game size: {size}"
    pygame_launcher.update_config(scale=size)
