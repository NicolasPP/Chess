import typing
import ttkbootstrap as ttk
from config.tk_config import *
from database.chess_db import ChessDataBase, CreateUserResult
from database.models import User
from launcher.tk.launcher_user import LauncherUser
from launcher.tk.components.play_comp import PlayButtons


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
    elo_label: ttk.Label
    games_played_label: ttk.Label

    def place(self) -> None:
        self.entry_frame.pack(expand=True)
        self.button_frame.pack(expand=True)

    def place_forget(self) -> None:
        self.entry_frame.pack_forget()
        self.button_frame.pack_forget()

    def place_log_in_entry(self) -> None:
        self.user_name_label.grid(row=0, column=0, pady=(0, SETTINGS_PAD // 2), padx=(0, SETTINGS_PAD // 2))
        self.user_name_entry.grid(row=0, column=1, pady=(0, SETTINGS_PAD // 2), padx=(SETTINGS_PAD // 2, 0))
        self.user_password_label.grid(row=1, column=0, pady=(SETTINGS_PAD // 2, 0), padx=(0, SETTINGS_PAD // 2))
        self.user_password_entry.grid(row=1, column=1, pady=(SETTINGS_PAD // 2, 0), padx=(SETTINGS_PAD // 2, 0))
        self.place_log_in_buttons()

    def place_log_in_buttons(self) -> None:
        self.log_in_button.pack(side=ttk.LEFT, expand=True)
        self.register_button.pack(side=ttk.LEFT, expand=True)

    def place_register_buttons(self) -> None:
        self.cancel_button.pack(side=ttk.LEFT, expand=True)
        self.create_user_button.pack(side=ttk.LEFT, expand=True)

    def place_forget_button(self) -> None:
        self.log_in_button.pack_forget()
        self.register_button.pack_forget()
        self.log_out_button.pack_forget()
        self.create_user_button.pack_forget()
        self.cancel_button.pack_forget()

    def place_forget_entry(self) -> None:
        self.user_name_label.grid_forget()
        self.user_name_entry.grid_forget()
        self.user_password_label.grid_forget()
        self.user_password_entry.grid_forget()

    def place_logged_in(self) -> None:
        self.elo_label.pack(side=ttk.TOP, expand=True)
        self.games_played_label.pack(side=ttk.TOP, expand=True)
        self.log_out_button.pack(side=ttk.TOP, expand=True)
        self.button_frame.pack(side=ttk.TOP, expand=True)

    def place_forget_logged_in(self) -> None:
        self.elo_label.pack_forget()
        self.log_out_button.pack_forget()
        self.button_frame.pack_forget()


class UserVars(typing.NamedTuple):
    is_database_up: ttk.BooleanVar
    user_name_var: ttk.StringVar
    user_password_var: ttk.StringVar
    error_var: ttk.StringVar
    elo_var: ttk.StringVar
    games_played_var: ttk.StringVar


class UserComponent:

    @staticmethod
    def get_vars() -> UserVars:
        return UserVars(ttk.BooleanVar(value=False), ttk.StringVar(), ttk.StringVar(), ttk.StringVar(), ttk.StringVar(),
                        ttk.StringVar())

    def __init__(self, parent: ttk.Frame, database: ChessDataBase, play_buttons: PlayButtons) -> None:
        self.frame: ttk.LabelFrame = ttk.LabelFrame(parent, text="Log In")
        self.vars: UserVars = UserComponent.get_vars()

        user_widgets: UserWidgets = self.create_user_widgets()

        user_widgets.user_password_entry.bind('<Return>', lambda e: handle_log_in(user_widgets, database, self.frame,
                                                                                  play_buttons.is_logged_in, self.vars))
        self.vars.is_database_up.trace_add('write', lambda v, i, m: is_database_up_callback(user_widgets, self.vars))

        self.set_commands(user_widgets, database, self.vars, play_buttons)

        user_widgets.place_log_in_entry()
        user_widgets.place()

    def get_frame(self) -> ttk.LabelFrame:
        return self.frame

    def set_commands(self, user_widgets: UserWidgets, database: ChessDataBase, user_vars: UserVars,
                     play_buttons: PlayButtons) -> None:
        user_widgets.register_button[ttk.COMMAND] = lambda: handle_register(user_widgets, self.frame, database,
                                                                            user_vars.is_database_up)
        user_widgets.cancel_button[ttk.COMMAND] = lambda: handle_cancel(user_widgets, self.frame)
        user_widgets.log_in_button[ttk.COMMAND] = lambda: handle_log_in(user_widgets, database, self.frame,
                                                                        play_buttons.is_logged_in, user_vars)
        user_widgets.create_user_button[ttk.COMMAND] = lambda: handle_create_user(user_widgets, database, self.frame,
                                                                                  user_vars)
        user_widgets.log_out_button[ttk.COMMAND] = lambda: handle_log_out(user_widgets, self.frame,
                                                                          play_buttons.is_logged_in)

    def create_user_widgets(self) -> UserWidgets:
        entry_frame: ttk.Frame = ttk.Frame(self.frame)
        button_frame: ttk.Frame = ttk.Frame(self.frame)

        user_name_entry: ttk.Entry = ttk.Entry(entry_frame, textvariable=self.vars.user_name_var)
        user_name_label: ttk.Label = ttk.Label(entry_frame, text="username: ")
        user_password_entry: ttk.Entry = ttk.Entry(entry_frame, textvariable=self.vars.user_password_var, show="*")
        user_password_label: ttk.Label = ttk.Label(entry_frame, text="password: ")

        log_in_button: ttk.Button = ttk.Button(button_frame, text="LOG IN")
        register_button: ttk.Button = ttk.Button(button_frame, text="REGISTER")

        create_user_button: ttk.Button = ttk.Button(button_frame, text="CREATE")
        cancel_button: ttk.Button = ttk.Button(button_frame, text="CANCEL")
        log_out_button: ttk.Button = ttk.Button(button_frame, text="LOG OUT")
        error_label: ttk.Label = ttk.Label(self.frame, textvariable=self.vars.error_var, foreground='red')
        elo_label: ttk.Label = ttk.Label(self.frame, textvariable=self.vars.elo_var, foreground='gold')
        games_played_label: ttk.Label = ttk.Label(self.frame, textvariable=self.vars.games_played_var)
        return UserWidgets(entry_frame, button_frame, user_name_entry, user_name_label, user_password_entry,
                           user_password_label, log_in_button, register_button, create_user_button, cancel_button,
                           log_out_button, error_label, elo_label, games_played_label)


def handle_log_in(user_widgets: UserWidgets, database: ChessDataBase, user_frame: ttk.LabelFrame,
                  is_logged_in: ttk.BooleanVar, user_vars: UserVars) -> None:
    if len(user_vars.user_name_var.get()) == 0: return
    if len(user_vars.user_password_var.get()) == 0: return

    if not user_vars.is_database_up.get():
        user_vars.is_database_up.set(database.test_connection())

    if not user_vars.is_database_up.get(): return

    user: User | None = database.log_in(user_vars.user_name_var.get(), user_vars.user_password_var.get())

    if user is None:
        user_vars.error_var.set("user name or password: incorrect")
        user_widgets.error_label.pack(expand=True)
    else:
        LauncherUser.log_in(user)
        is_logged_in.set(True)

        user_widgets.place_forget_button()
        user_widgets.place_forget()
        user_widgets.error_label.pack_forget()
        user_widgets.place_logged_in()
        set_elo_label(user_vars)
        set_game_stats(user_vars, database)
        user_frame["text"] = user.u_name

    user_vars.user_name_var.set("")
    user_vars.user_password_var.set("")


def handle_register(user_widgets: UserWidgets, user_frame: ttk.LabelFrame, database: ChessDataBase,
                    is_database_up: ttk.BooleanVar) -> None:
    if not is_database_up.get():
        is_database_up.set(database.test_connection())

    if not is_database_up.get(): return

    user_widgets.place_forget_button()
    user_widgets.error_label.pack_forget()
    user_widgets.place_register_buttons()

    user_frame["text"] = "Create User"


def handle_create_user(user_widgets: UserWidgets, database: ChessDataBase, user_frame: ttk.LabelFrame,
                       user_vars: UserVars) -> None:
    create_user_result: CreateUserResult = database.create_user(user_vars.user_name_var.get(),
                                                                user_vars.user_password_var.get())

    if create_user_result is CreateUserResult.SUCCESS:
        handle_cancel(user_widgets, user_frame)
        user_vars.user_name_var.set("")
        user_vars.user_password_var.set("")
        return

    elif create_user_result is CreateUserResult.INVALID_USER_NAME:
        user_vars.error_var.set("user name only alphanumeric")

    elif create_user_result is CreateUserResult.USER_NAME_TAKEN:
        user_vars.error_var.set("user name taken")

    elif create_user_result is CreateUserResult.INVALID_PASSWORD:
        user_vars.error_var.set("password cannot be empty")

    user_widgets.error_label.pack(expand=True)


def handle_cancel(user_widgets: UserWidgets, user_frame: ttk.LabelFrame) -> None:
    user_widgets.place_forget_button()
    user_widgets.error_label.pack_forget()
    user_widgets.place_log_in_entry()
    user_frame["text"] = "Log In"


def handle_log_out(user_widgets: UserWidgets, user_frame: ttk.LabelFrame, is_logged_in: ttk.BooleanVar) -> None:
    user_widgets.place_forget_logged_in()
    user_widgets.place_log_in_buttons()
    user_widgets.place()
    user_frame["text"] = "Log In"
    LauncherUser.log_out()
    is_logged_in.set(False)


def is_database_up_callback(user_widgets: UserWidgets, user_vars: UserVars) -> None:
    is_database: bool = user_vars.is_database_up.get()
    state = ttk.NORMAL if is_database else ttk.DISABLED
    user_widgets.create_user_button["state"] = state
    user_widgets.log_in_button["state"] = state
    user_widgets.log_out_button["state"] = state
    user_widgets.register_button["state"] = state

    if is_database: return

    user_vars.error_var.set("database is not available")
    user_widgets.error_label.pack(expand=True)


def set_elo_label(user_vars: UserVars) -> None:
    user_vars.elo_var.set(f"elo : {LauncherUser.get_user().elo}")


def set_game_stats(user_var: UserVars, database: ChessDataBase) -> None:
    game_num: int = len(database.get_users_game(LauncherUser.get_user()))
    user_var.games_played_var.set(f"games played: {game_num}")
