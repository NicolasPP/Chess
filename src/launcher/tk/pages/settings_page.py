import typing

import tkinter as tk
import ttkbootstrap as ttk
from launcher.tk.page_frame import PageFrame
from launcher.tk.page_manager import PageManager


class SettingsPageButtons(typing.NamedTuple):
    back: ttk.Button


class SettingsPage(PageFrame):
    def __init__(self, parent_frame: tk.Frame, page_manager: PageManager) -> None:
        super().__init__(parent_frame)
        buttons = self.create_buttons(page_manager)
        label = ttk.Label(self, text="Settings", font=("Verdana", 20))
        label.pack()
        buttons.back.pack()

    def create_buttons(self, page_manager: PageManager) -> SettingsPageButtons:
        back_button: ttk.Button = ttk.Button(self, text="Back", command=lambda: page_manager.show_page("StartPage"))
        return SettingsPageButtons(back_button)