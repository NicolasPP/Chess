import enum
import typing
import tkinter as tk
from ttkbootstrap import ttk
from config.tk_config import *
from database.chess_db import ChessDataBase, CreateUserResult
from database.models import User
from launcher.tk.launcher_user import LauncherUser
from launcher.tk.components.tk_component import Component


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
        self.log_in_button.pack(side=tk.LEFT, expand=True)
        self.register_button.pack(side=tk.LEFT, expand=True)

    def place_register_buttons(self) -> None:
        self.cancel_button.pack(side=tk.LEFT, expand=True)
        self.create_user_button.pack(side=tk.LEFT, expand=True)

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
        self.elo_label.pack(side=tk.TOP, expand=True)
        self.games_played_label.pack(side=tk.TOP, expand=True)
        self.log_out_button.pack(side=tk.TOP, expand=True)
        self.button_frame.pack(side=tk.TOP, expand=True)

    def place_forget_logged_in(self) -> None:
        self.elo_label.pack_forget()
        self.games_played_label.pack_forget()
        self.log_out_button.pack_forget()
        self.button_frame.pack_forget()


class UserVars(typing.NamedTuple):
    is_database_up: tk.BooleanVar
    user_name_var: tk.StringVar
    user_password_var: tk.StringVar
    error_var: tk.StringVar
    elo_var: tk.StringVar
    games_played_var: tk.StringVar


class UserComponentState(enum.Enum):
    LOG_IN = enum.auto()
    CREATE_USER = enum.auto()
    LOG_OUT = enum.auto()


class UserComponent(Component):

    @staticmethod
    def get_vars() -> UserVars:
        return UserVars(tk.BooleanVar(value=False), tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar(),
                        tk.StringVar())

    def __init__(self, parent: ttk.Frame, database: ChessDataBase, is_logged_in: tk.BooleanVar) -> None:
        super().__init__(parent, "Log In")
        self.state: UserComponentState = UserComponentState.LOG_IN
        self.vars: UserVars = UserComponent.get_vars()
        self.widgets: UserWidgets = self.create_user_widgets()

        self.widgets.user_password_entry.bind('<Return>', lambda e: self.handle_pass_entry_enter(database,
                                                                                                 is_logged_in))
        self.vars.is_database_up.trace_add('write', lambda v, i, m: is_database_up_callback(self.widgets, self.vars))

        self.set_commands(database, is_logged_in)

        self.widgets.place_log_in_entry()
        self.widgets.place()

    def set_commands(self, database: ChessDataBase, is_logged_in: tk.BooleanVar) -> None:
        self.widgets.register_button.configure(command=lambda: self.handle_register(database))
        self.widgets.cancel_button.configure(command=lambda: self.handle_cancel())
        self.widgets.log_in_button.configure(command=lambda: self.handle_log_in(database, is_logged_in))
        self.widgets.create_user_button.configure(command=lambda: self.handle_create_user(database))
        self.widgets.log_out_button.configure(command=lambda: self.handle_log_out(is_logged_in))

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

    def handle_log_in(self, database: ChessDataBase, is_logged_in: tk.BooleanVar) -> None:
        if self.state is not UserComponentState.LOG_IN: return
        if len(self.vars.user_name_var.get()) == 0: return
        if len(self.vars.user_password_var.get()) == 0: return

        if not self.vars.is_database_up.get():
            self.vars.is_database_up.set(database.test_connection())

        if not self.vars.is_database_up.get(): return

        user: User | None = database.log_in(self.vars.user_name_var.get(), self.vars.user_password_var.get())

        if user is None:
            self.vars.error_var.set("user name or password: incorrect")
            self.widgets.error_label.pack(expand=True)
        else:
            self.state = UserComponentState.LOG_OUT
            LauncherUser.log_in(user)
            is_logged_in.set(True)
            self.widgets.place_forget_button()
            self.widgets.place_forget()
            self.widgets.error_label.pack_forget()
            self.widgets.place_logged_in()
            set_elo_label(self.vars)
            set_game_stats(self.vars, database)
            self.set_title(user.u_name)

        self.vars.user_name_var.set("")
        self.vars.user_password_var.set("")

    def handle_log_out(self, is_logged_in: tk.BooleanVar) -> None:
        if self.state is not UserComponentState.LOG_OUT: return
        self.widgets.place_forget_logged_in()
        self.widgets.place_log_in_buttons()
        self.widgets.place()
        self.set_title("Log In")
        LauncherUser.log_out()
        is_logged_in.set(False)
        self.state = UserComponentState.LOG_IN

    def handle_register(self, database: ChessDataBase) -> None:
        if self.state is not UserComponentState.LOG_IN: return

        if not self.vars.is_database_up.get():
            self.vars.is_database_up.set(database.test_connection())

        if not self.vars.is_database_up.get(): return

        self.state = UserComponentState.CREATE_USER
        self.widgets.place_forget_button()
        self.widgets.error_label.pack_forget()
        self.widgets.place_register_buttons()

        self.frame.configure(text="Create User")

    def handle_cancel(self) -> None:
        if self.state is not UserComponentState.CREATE_USER: return
        self.state = UserComponentState.LOG_IN
        self.widgets.place_forget_button()
        self.widgets.error_label.pack_forget()
        self.widgets.place_log_in_entry()
        self.frame.configure(text="Log In")

    def handle_create_user(self, database: ChessDataBase) -> None:
        if self.state is not UserComponentState.CREATE_USER: return
        create_user_result: CreateUserResult = database.create_user(self.vars.user_name_var.get(),
                                                                    self.vars.user_password_var.get())

        if create_user_result is CreateUserResult.SUCCESS:
            self.handle_cancel()
            self.vars.user_name_var.set("")
            self.vars.user_password_var.set("")
            return

        elif create_user_result is CreateUserResult.INVALID_USER_NAME:
            self.vars.error_var.set("user name only alphanumeric")

        elif create_user_result is CreateUserResult.USER_NAME_TAKEN:
            self.vars.error_var.set("user name taken")

        elif create_user_result is CreateUserResult.INVALID_PASSWORD:
            self.vars.error_var.set("password cannot be empty")

        self.widgets.error_label.pack(expand=True)

    def handle_pass_entry_enter(self, database: ChessDataBase, is_logged_in: tk.BooleanVar) -> None:
        if self.state is UserComponentState.LOG_IN:
            self.handle_log_in(database, is_logged_in)

        elif self.state is UserComponentState.CREATE_USER:
            self.handle_create_user(database)


def is_database_up_callback(user_widgets: UserWidgets, user_vars: UserVars) -> None:
    is_database: bool = user_vars.is_database_up.get()
    state = tk.NORMAL if is_database else tk.DISABLED
    user_widgets.create_user_button.configure(state=state)
    user_widgets.log_in_button.configure(state=state)
    user_widgets.log_out_button.configure(state=state)
    user_widgets.register_button.configure(state=state)

    if is_database: return

    user_vars.error_var.set("database is not available")
    user_widgets.error_label.pack(expand=True)


def set_elo_label(user_vars: UserVars) -> None:
    user_vars.elo_var.set(f"elo : {LauncherUser.get_user().elo}")


def set_game_stats(user_var: UserVars, database: ChessDataBase) -> None:
    game_num: int = len(database.get_users_game(LauncherUser.get_user()))
    user_var.games_played_var.set(f"games played: {game_num}")
