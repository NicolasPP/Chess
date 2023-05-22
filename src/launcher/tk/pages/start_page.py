import typing
import tkinter as tk
import ttkbootstrap as ttk
from launcher.tk.page_frame import PageFrame
from launcher.tk.page_manager import PageManager
from config.tk_config import *
from chess.bot.chess_bot_stockfish import StockFishBot
from launcher.pg.pg_launcher import PossibleConfigValues, ChessPygameLauncher
from database.chess_db import ChessDataBase, CreateUserResult
from database.models import User
from launcher.tk.user import LauncherUser


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


class UserWidgets(typing.NamedTuple):
    entry_frame: ttk.Frame
    button_frame: ttk.Frame
    user_name_entry: ttk.Entry
    user_name_label: ttk.Label
    user_password_entry: ttk.Entry
    user_password_label: ttk.Label
    log_in_button: ttk.Button
    register_button: ttk.Button
    create_user_button: ttk.Button
    cancel_button: ttk.Button
    log_out_button: ttk.Button
    error_label: ttk.Label


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

    @staticmethod
    def create_user_widgets(user_frame: ttk.LabelFrame, user_name_var: ttk.StringVar, user_password_var: ttk.StringVar,
                            error_var: ttk.StringVar) -> UserWidgets:
        entry_frame: ttk.Frame = ttk.Frame(user_frame)
        button_frame: ttk.Frame = ttk.Frame(user_frame)

        user_name_entry: ttk.Entry = ttk.Entry(entry_frame, textvariable=user_name_var)
        user_name_label: ttk.Label = ttk.Label(entry_frame, text="user name:")
        user_password_entry: ttk.Entry = ttk.Entry(entry_frame, textvariable=user_password_var, show="*")
        user_password_label: ttk.Label = ttk.Label(entry_frame, text="password:")

        log_in_button: ttk.Button = ttk.Button(button_frame, text="LOG IN", command=lambda: print("LOG IN"))
        register_button: ttk.Button = ttk.Button(button_frame, text="REGISTER")

        create_user_button: ttk.Button = ttk.Button(button_frame, text="CREATE")
        cancel_button: ttk.Button = ttk.Button(button_frame, text="CANCEL")
        log_out_button: ttk.Button = ttk.Button(button_frame, text="LOG OUT")
        error_label: ttk.Label = ttk.Label(user_frame, textvariable=error_var, foreground='red')
        return UserWidgets(entry_frame, button_frame, user_name_entry, user_name_label, user_password_entry,
                           user_password_label, log_in_button, register_button, create_user_button, cancel_button,
                           log_out_button, error_label)

    def __init__(self, parent_frame: tk.Frame, page_manager: PageManager, is_bot_valid: ttk.BooleanVar,
                 pg_launcher: ChessPygameLauncher, database: ChessDataBase) -> None:
        super().__init__(parent_frame)
        play_frame: ttk.LabelFrame = ttk.LabelFrame(self, text='Play')
        settings_frame: ttk.LabelFrame = ttk.LabelFrame(self, text='Settings')
        user_frame: ttk.LabelFrame = ttk.LabelFrame(self, text="Log In")

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        play_buttons = StartPage.create_play_buttons(page_manager, play_frame)
        play_frame.grid(row=0, column=0, sticky=ttk.NSEW, padx=START_PAGE_FRAME_PAD, pady=START_PAGE_FRAME_PAD)
        play_buttons.online.pack(side=ttk.LEFT, expand=True, anchor=ttk.CENTER)
        play_buttons.offline.pack(side=ttk.LEFT, expand=True, anchor=ttk.CENTER)

        path_entry_str: ttk.StringVar = ttk.StringVar(value="stock fish engine path")
        settings_widgets = StartPage.create_settings_widgets(settings_frame, path_entry_str, pg_launcher)

        settings_frame.grid(row=0, column=1, rowspan=2, sticky=ttk.NSEW, padx=START_PAGE_FRAME_PAD,
                            pady=START_PAGE_FRAME_PAD)
        settings_widgets.create_bot[ttk.COMMAND] = lambda: create_bot_command(settings_widgets, is_bot_valid,
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

        user_name_var: ttk.StringVar = ttk.StringVar()
        user_password_var: ttk.StringVar = ttk.StringVar()
        error_var: ttk.StringVar = ttk.StringVar()
        user_widgets: UserWidgets = StartPage.create_user_widgets(user_frame, user_name_var, user_password_var,
                                                                  error_var)
        user_frame.grid(row=1, column=0, sticky=ttk.NSEW, padx=START_PAGE_FRAME_PAD, pady=START_PAGE_FRAME_PAD)
        user_widgets.register_button[ttk.COMMAND] = lambda: handle_register(user_widgets, user_frame)
        user_widgets.cancel_button[ttk.COMMAND] = lambda: handle_cancel(user_widgets, user_frame)
        user_widgets.log_in_button[ttk.COMMAND] = lambda: handle_log_in(user_widgets, user_name_var, user_password_var,
                                                                        error_var, database, user_frame)
        user_widgets.create_user_button[ttk.COMMAND] = lambda: handle_create_user(user_widgets, user_name_var,
                                                                                  user_password_var, error_var,
                                                                                  database, user_frame)
        user_widgets.log_out_button[ttk.COMMAND] = lambda: handle_log_out(user_widgets, user_frame)

        user_widgets.user_name_label.grid(row=0, column=0, pady=(0, SETTINGS_PAD // 2), padx=(0, SETTINGS_PAD // 2))
        user_widgets.user_name_entry.grid(row=0, column=1, pady=(0, SETTINGS_PAD // 2), padx=(SETTINGS_PAD // 2, 0))
        user_widgets.user_password_label.grid(row=1, column=0, pady=(SETTINGS_PAD // 2, 0), padx=(0, SETTINGS_PAD // 2))
        user_widgets.user_password_entry.grid(row=1, column=1, pady=(SETTINGS_PAD // 2, 0), padx=(SETTINGS_PAD // 2, 0))

        user_widgets.log_in_button.pack(side=ttk.LEFT, expand=True)
        user_widgets.register_button.pack(side=ttk.LEFT, expand=True)

        user_widgets.entry_frame.pack(expand=True)
        user_widgets.button_frame.pack(expand=True)


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


def handle_log_in(user_widgets: UserWidgets, user_name_var: ttk.StringVar, user_password_var: ttk.StringVar,
                  error_var: ttk.StringVar, database: ChessDataBase, user_frame: ttk.LabelFrame) -> None:
    user: User | None = database.log_in(user_name_var.get(), user_password_var.get())
    if user is None:
        error_var.set("user name or password: incorrect")
        user_widgets.error_label.pack(expand=True)
    else:
        LauncherUser.log_in(user)
        user_widgets.entry_frame.pack_forget()
        user_widgets.log_in_button.pack_forget()
        user_widgets.register_button.pack_forget()
        user_widgets.error_label.pack_forget()
        user_widgets.log_out_button.pack(expand=True)
        user_frame["text"] = user.u_name
    user_name_var.set("")
    user_password_var.set("")


def handle_register(user_widgets: UserWidgets, user_frame: ttk.LabelFrame) -> None:
    # clear button frame
    user_widgets.log_in_button.pack_forget()
    user_widgets.register_button.pack_forget()
    user_widgets.error_label.pack_forget()

    # pack new buttons
    user_widgets.cancel_button.pack(side=ttk.LEFT, expand=True)
    user_widgets.create_user_button.pack(side=ttk.LEFT, expand=True)

    user_frame["text"] = "Create User"


def handle_create_user(user_widgets: UserWidgets, user_name_var: ttk.StringVar, user_password_var: ttk.StringVar,
                       error_var: ttk.StringVar, database: ChessDataBase, user_frame: ttk.LabelFrame) -> None:
    create_user_result: CreateUserResult = database.create_user(user_name_var.get(), user_password_var.get())

    if create_user_result is CreateUserResult.SUCCESS:
        handle_cancel(user_widgets, user_frame)
        user_name_var.set("")
        user_password_var.set("")
        return

    elif create_user_result is CreateUserResult.INVALID_USER_NAME:
        error_var.set("user name only alphanumeric")

    elif create_user_result is CreateUserResult.USER_NAME_TAKEN:
        error_var.set("user name taken")

    elif create_user_result is CreateUserResult.INVALID_PASSWORD:
        error_var.set("password cannot be empty")

    user_widgets.error_label.pack(expand=True)


def handle_cancel(user_widgets: UserWidgets, user_frame: ttk.LabelFrame) -> None:
    # clear button frame
    user_widgets.cancel_button.pack_forget()
    user_widgets.create_user_button.pack_forget()
    user_widgets.error_label.pack_forget()

    # pack new buttons
    user_widgets.log_in_button.pack(side=ttk.LEFT, expand=True)
    user_widgets.register_button.pack(side=ttk.LEFT, expand=True)

    user_frame["text"] = "Log In"


def handle_log_out(user_widgets: UserWidgets, user_frame: ttk.LabelFrame) -> None:
    # clear
    user_widgets.log_out_button.pack_forget()
    user_widgets.button_frame.pack_forget()

    # pack
    user_widgets.log_in_button.pack(side=ttk.LEFT, expand=True)
    user_widgets.register_button.pack(side=ttk.LEFT, expand=True)

    user_widgets.entry_frame.pack(expand=True)
    user_widgets.button_frame.pack(expand=True)

    user_frame["text"] = "Log In"
    LauncherUser.log_out()
