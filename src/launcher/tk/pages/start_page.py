import typing
import tkinter as tk
import ttkbootstrap as ttk
from launcher.tk.page_frame import PageFrame
from launcher.tk.page_manager import PageManager
from config.tk_config import *
from chess.bot.chess_bot_stockfish import StockFishBot
from launcher.pg.pg_launcher import PossibleConfigValues, PygameChessLauncher


class PlayButtons(typing.NamedTuple):
    online: ttk.Button
    offline: ttk.Button


class SettingsWidgets(typing.NamedTuple):
    engine_valid: ttk.Label
    path_entry: ttk.Entry
    create_bot: ttk.Button
    theme_options: ttk.Combobox
    theme_label: ttk.Label
    asset_options: ttk.Combobox
    asset_label: ttk.Label
    scale_options: ttk.Combobox
    scale_label: ttk.Label


class StartPage(PageFrame):

    @staticmethod
    def create_play_buttons(page_manger: PageManager, play_frame: ttk.LabelFrame) -> PlayButtons:
        online_button: ttk.Button = ttk.Button(play_frame, text="Online",
                                               command=lambda: page_manger.show_page("OnlinePage"))
        offline_button: ttk.Button = ttk.Button(play_frame, text="Offline",
                                                command=lambda: page_manger.show_page("OfflinePage"))
        return PlayButtons(online_button, offline_button)

    @staticmethod
    def create_settings_widgets(settings_frame: ttk.LabelFrame, path_entry_str: ttk.StringVar) -> SettingsWidgets:
        engine_valid: ttk.Label = ttk.Label(settings_frame, text="Stock Fish ready!", font=(FONT_NAME, 13))
        path_entry: ttk.Entry = ttk.Entry(settings_frame, textvariable=path_entry_str)
        path_entry.bind("<Button>", lambda e: path_entry_str.set(''))
        create_bot: ttk.Button = ttk.Button(settings_frame, text="create bot")

        theme_label: ttk.Label = ttk.Label(settings_frame, text="Theme: ")
        theme_options: ttk.Combobox = ttk.Combobox(settings_frame, values=["1", "2", "3", "4", "RANDOM"],
                                                   state="readonly")
        theme_options.set("RANDOM")

        asset_label: ttk.Label = ttk.Label(settings_frame, text="Asset: ")
        asset_options: ttk.Combobox = ttk.Combobox(settings_frame, values=["LARGE", "SMALL"], state="readonly")
        asset_options.set("LARGE")

        scale_label: ttk.Label = ttk.Label(settings_frame, text="Size: ")
        scale_options: ttk.Combobox = ttk.Combobox(settings_frame, values=[str(x) for x in range(3, 9)],
                                                   state="readonly")
        scale_options.set("4")
        return SettingsWidgets(engine_valid, path_entry, create_bot, theme_options, theme_label, asset_options,
                               asset_label, scale_options, scale_label)

    def __init__(self, parent_frame: tk.Frame, page_manager: PageManager, is_bot_valid: ttk.BooleanVar,
                 pg_launcher: PygameChessLauncher) -> None:
        super().__init__(parent_frame)
        play_frame: ttk.LabelFrame = ttk.LabelFrame(self, text='Play')
        settings_frame: ttk.LabelFrame = ttk.LabelFrame(self, text='Settings')
        user_frame: ttk.LabelFrame = ttk.LabelFrame(self, text='User')

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=5)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=10)

        play_buttons = StartPage.create_play_buttons(page_manager, play_frame)
        play_frame.grid(row=0, column=0, sticky="news", padx=5, pady=5)
        play_buttons.online.pack(side="left", expand=True, anchor='center')
        play_buttons.offline.pack(side="left", expand=True, anchor='center')

        path_entry_str: ttk.StringVar = ttk.StringVar(value="stock fish engine path")
        settings_widgets = StartPage.create_settings_widgets(settings_frame, path_entry_str)

        settings_frame.grid(row=0, column=1, rowspan=2, sticky="news", padx=5, pady=5)
        settings_widgets.create_bot["command"] = lambda: create_bot_command(settings_widgets, is_bot_valid,
                                                                            path_entry_str)

        is_bot_valid.set(StockFishBot.create_bot())
        # if is_bot_valid.get():
        #     settings_widgets.engine_valid.pack(expand=True)
        # else:
        #     settings_widgets.path_entry.pack(expand=True)
        #     settings_widgets.create_bot.pack(expand=True)

        settings_frame.grid_columnconfigure(0, weight=1)
        settings_frame.grid_columnconfigure(1, weight=1)

        menubutton = ttk.Menubutton(settings_frame, text='hello')
        menu = ttk.Menu(menubutton)
        menu.add_radiobutton(value="Nicolas", label="Nicolas", background=BG_DARK, foreground=FG_DARK,
                             command=lambda: configure_pygame_launcher(pg_launcher, scale=6.0))

        menubutton['menu'] = menu

        menubutton.pack()

        # settings_widgets.scale_label.grid(row=0, column=0, sticky='news', padx=10, pady=10)
        # settings_widgets.scale_options.grid(row=0, column=1, sticky='news', padx=10, pady=10)
        #
        # settings_widgets.asset_label.grid(row=1, column=0, sticky='news', padx=10, pady=10)
        # settings_widgets.asset_options.grid(row=1, column=1, sticky='news', padx=10, pady=10)
        #
        # settings_widgets.theme_label.grid(row=2, column=0, sticky='news', padx=10, pady=10)
        # settings_widgets.theme_options.grid(row=2, column=1, sticky='news', padx=10, pady=10)

        user_frame.grid(row=1, column=0, sticky="news", padx=5, pady=5)


def create_bot_command(settings_widgets: SettingsWidgets, is_bot_valid: ttk.BooleanVar,
                       path_entry_str: ttk.StringVar) -> None:
    if StockFishBot.create_bot(path_entry_str.get()):
        settings_widgets.create_bot.pack_forget()
        settings_widgets.path_entry.pack_forget()
        settings_widgets.asset_options.pack_forget()
        settings_widgets.theme_options.pack_forget()
        settings_widgets.scale_options.pack_forget()
        settings_widgets.engine_valid.pack(expand=True)
        settings_widgets.asset_options.pack(expand=True)
        settings_widgets.theme_options.pack(expand=True)
        settings_widgets.scale_options.pack(expand=True)
        is_bot_valid.set(True)
    else:
        path_entry_str.set("Path Incorrect")


def configure_pygame_launcher(pygame_launcher: PygameChessLauncher, **args: PossibleConfigValues) -> None:
    pygame_launcher.update_config(**args)
