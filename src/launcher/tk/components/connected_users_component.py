import tkinter as tk
import typing

import ttkbootstrap
from ttkbootstrap import ttk

from config.tk_config import CANVAS_WINDOW_POS
from config.tk_config import SCROLLBAR_WIDTH
from config.tk_config import USER_CARD_SPACING
from config.tk_config import LAUNCHER_PAD
from config.tk_config import DEFAULT_CARD_HEIGHT
from config.tk_config import MAX_CONNECTIONS
from launcher.tk.components.tk_component import Component
from launcher.tk.global_vars import GlobalUserVars
from launcher.tk.launcher_user import LauncherUser


class ConnectedUsersWidgets(typing.NamedTuple):
    container: ttk.Frame
    scroll_bar: ttk.Scrollbar
    canvas: tk.Canvas
    window_frame: ttk.Frame
    window_id: int


class ConnectedUserCard(typing.NamedTuple):
    user_name: str
    card_frame: ttk.Frame
    select_button: ttk.Button
    elo_label: ttk.Label


class CanvasWindowRect(typing.NamedTuple):
    x: int
    y: int
    width: int
    height: int


class ConnectedUsersComponent(Component):

    def __init__(self, parent: ttk.Frame) -> None:
        super().__init__(parent, "Connected Users")
        GlobalUserVars.get().get_var(GlobalUserVars.connected_users).trace_add(
            "write", lambda v, i, m: self.update_connected_users()
        )
        self.widgets: ConnectedUsersWidgets = self.create_widgets()
        self.user_cards: list[ConnectedUserCard] = []

        self.pack_user_cards()

        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        self.widgets.scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
        self.widgets.canvas.pack(side=tk.LEFT, fill=tk.BOTH)
        self.widgets.container.grid(sticky=tk.NSEW, pady=20, padx=20)

    def create_widgets(self) -> ConnectedUsersWidgets:
        container: ttk.Frame = ttk.Frame(self.frame)
        scroll_bar: ttk.Scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, style=ttkbootstrap.WARNING)
        canvas: tk.Canvas = tk.Canvas(container)
        window_frame: ttk.Frame = ttk.Frame(container, height=get_window_frame_height())
        window_id: int = canvas.create_window(*CANVAS_WINDOW_POS, window=window_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scroll_bar.set)
        scroll_bar.configure(command=canvas.yview)
        container.bind("<Configure>", lambda event: self.handle_container_resize(event.width))
        return ConnectedUsersWidgets(container, scroll_bar, canvas, window_frame, window_id)

    def handle_exit(self) -> None:
        self.widgets.container.unbind("<Configure>")

    def get_canvas_window_rect(self) -> CanvasWindowRect:
        return CanvasWindowRect(*self.widgets.canvas.bbox(self.widgets.window_id))

    def handle_container_resize(self, event_width: int) -> None:
        # setting the size of the window_frame everytime we resize container. seems to be the
        # only way of prevent the created_window from shrinking to children combined height
        self.widgets.canvas.itemconfig(self.widgets.window_id, height=get_window_frame_height())
        self.widgets.canvas.itemconfig(self.widgets.window_id, width=event_width - SCROLLBAR_WIDTH)

    def update_connected_users(self) -> None:
        users_info: list[tuple[str, str]] = []
        for user_info in GlobalUserVars.get().get_var(GlobalUserVars.connected_users).get().split():
            user_name, user_elo = user_info.split("-")
            if user_name == LauncherUser.get_user().u_name: continue
            users_info.append((user_name, user_elo))

        self.destroy_user_cards()
        self.user_cards = self.create_user_cards(users_info)
        self.pack_user_cards()

    def destroy_user_cards(self) -> None:
        for user_card in self.user_cards:
            user_card.card_frame.destroy()

    def create_user_cards(self, users_info: list[tuple[str, str]]) -> list[ConnectedUserCard]:
        connected_users: list[ConnectedUserCard] = []
        for user_info in users_info:
            user_name, user_elo = user_info
            card_frame: ttk.Frame = ttk.Frame(self.widgets.window_frame)
            select_button: ttk.Button = ttk.Button(card_frame, text=user_name)
            elo_label: ttk.Label = ttk.Label(card_frame, text=f"elo : {user_elo}")
            connected_users.append(
                ConnectedUserCard(user_name, card_frame, select_button, elo_label)
            )
        return connected_users

    def get_scroll_region_height(self) -> int:
        self.widgets.window_frame.update()
        spacing_height: int = USER_CARD_SPACING * len(self.widgets.window_frame.children.values()) * 2
        children_height: int = sum([child.winfo_height() for child in self.widgets.window_frame.children.values()])
        return spacing_height + children_height

    def update_scroll_region(self) -> None:
        height: int = self.get_scroll_region_height()
        self.widgets.canvas.configure(scrollregion=(0, 0, 0, height))

    def pack_user_cards(self) -> None:
        for user_card in self.user_cards:
            user_card.elo_label.pack(side=tk.LEFT, expand=True)
            user_card.select_button.pack(side=tk.LEFT, expand=True)
            user_card.card_frame.pack(padx=LAUNCHER_PAD, pady=USER_CARD_SPACING)
        self.update_scroll_region()


def get_window_frame_height() -> int:
    return MAX_CONNECTIONS * DEFAULT_CARD_HEIGHT
