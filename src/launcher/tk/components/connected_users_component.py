import typing

import tkinter as tk

import ttkbootstrap
from ttkbootstrap import ttk

from launcher.tk.components.tk_component import Component

from config.tk_config import CANVAS_WINDOW_POS
from config.tk_config import SCROLLBAR_WIDTH


class ConnectedUsersWidgets(typing.NamedTuple):
    container: ttk.Frame
    scroll_bar: ttk.Scrollbar
    canvas: tk.Canvas
    window_frame: ttk.Frame
    window_id: int


class CanvasWindowRect(typing.NamedTuple):
    x: int
    y: int
    width: int
    height: int


class ConnectedUsersComponent(Component):

    def __init__(self, parent: ttk.Frame) -> None:
        super().__init__(parent, "Connected Users")
        self.widgets: ConnectedUsersWidgets = self.create_widgets()

        for i in range(10):
            ttk.Button(self.widgets.window_frame, text=f"im {i}").pack(expand=True)
        self.widgets.window_frame.update()
        self.widgets.canvas.configure(scrollregion=(0, 0, 0, self.widgets.window_frame.winfo_height()))

        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        self.widgets.scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
        self.widgets.canvas.pack(side=tk.LEFT, fill=tk.BOTH)
        self.widgets.container.grid(sticky=tk.NSEW, pady=20, padx=20)

    def create_widgets(self) -> ConnectedUsersWidgets:
        container: ttk.Frame = ttk.Frame(self.frame)
        scroll_bar: ttk.Scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, style=ttkbootstrap.WARNING)
        canvas: tk.Canvas = tk.Canvas(container)
        window_frame: ttk.Frame = ttk.Frame(container)
        window_id: int = canvas.create_window(*CANVAS_WINDOW_POS, window=window_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scroll_bar.set)
        scroll_bar.configure(command=canvas.yview)
        container.bind("<Configure>", self.handle_container_resize)
        return ConnectedUsersWidgets(container, scroll_bar, canvas, window_frame, window_id)

    def handle_exit(self) -> None:
        self.widgets.container.unbind("<Configure>")

    def get_canvas_window_rect(self) -> CanvasWindowRect:
        return CanvasWindowRect(*self.widgets.canvas.bbox(self.widgets.window_id))

    def handle_container_resize(self, event: tk.Event) -> None:
        canvas_window_rect: CanvasWindowRect = self.get_canvas_window_rect()
        if event.height > canvas_window_rect.height:
            self.widgets.canvas.itemconfig(self.widgets.window_id, height=event.height)
            self.widgets.canvas.configure(scrollregion=(0, 0, 0, event.height))

        self.widgets.canvas.itemconfig(self.widgets.window_id, width=event.width - SCROLLBAR_WIDTH)
