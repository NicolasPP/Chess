import functools
import typing

import tkinter as tk

import ttkbootstrap
from ttkbootstrap import ttk

from launcher.tk.components.tk_component import Component
from config.tk_config import BG_DARK
from config.tk_config import FG_DARK
from config.tk_config import CONNECTED_USERS_POS


class ConnectedUsersWidgets(typing.NamedTuple):
    users_canvas: tk.Canvas
    window_frame: ttk.Frame
    scrollbar: ttk.Scrollbar


class ConnectedUserCard(typing.NamedTuple):
    user_name: str
    card_frame: ttk.Frame
    button: ttk.Radiobutton


class ConnectedUserVars(typing.NamedTuple):
    users_var: tk.StringVar


class ConnectedUsersComponent(Component):
    def __init__(self, parent: ttk.Frame) -> None:
        super().__init__(parent, "Connected Users")
        f = ttk.Frame(self.frame)
        self.vars: ConnectedUserVars = create_vars()
        self.widgets: ConnectedUsersWidgets = self.create_widgets(f)
        self.user_cards: list[ConnectedUserCard] = []

        for user in ["nicolas", "gus", "ron", "son", "mil", "nicolas", "gus", "ron", "son", "mil", "nicolas", "gus", "ron", "son", "mil"]:
            card_frame: ttk.Frame = ttk.Frame(self.widgets.window_frame)
            radio_button: ttk.Radiobutton = ttk.Radiobutton(self.widgets.window_frame, text=user, value=user,
                                                            style=ttkbootstrap.TOOLBUTTON, variable=self.vars.users_var)
            self.user_cards.append(ConnectedUserCard(user, card_frame, radio_button))

        self.update_connected_users()

        self.widgets.window_frame.update()
        self.widgets.users_canvas.configure(yscrollcommand=self.widgets.scrollbar.set,
                                            scrollregion="0 0 0 %s" % self.widgets.window_frame.winfo_width())

        self.widgets.users_canvas.pack(side=tk.LEFT)
        self.widgets.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        f.pack()

    def get_scroll_width(self) -> int:
        return self.frame.winfo_width()

    def get_scroll_height(self) -> int:
        return self.frame.winfo_height()

    def update_connected_users(self) -> None:
        for user_card in self.user_cards:
            user_card.button.pack(expand=True)
            user_card.card_frame.pack(expand=True, fill=tk.X)

    def create_widgets(self, f) -> ConnectedUsersWidgets:
        users_canvas: tk.Canvas = tk.Canvas(f, width=self.get_scroll_width(), height=self.get_scroll_height())
        window_frame: ttk.Frame = ttk.Frame(users_canvas, width=self.get_scroll_width(), height=self.get_scroll_height())
        scrollbar: ttk.Scrollbar = ttk.Scrollbar(f, orient=tk.VERTICAL, command=users_canvas.yview,
                                                 style=ttkbootstrap.WARNING)
        users_canvas.create_window(CONNECTED_USERS_POS, window=window_frame, anchor=tk.NW)
        return ConnectedUsersWidgets(users_canvas, window_frame, scrollbar)


def create_vars() -> ConnectedUserVars:
    return ConnectedUserVars(tk.StringVar())
