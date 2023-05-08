import typing

import tkinter as tk
import ttkbootstrap as ttk
from launcher.tk.page_frame import PageFrame
from launcher.tk.page_manager import PageManager


class OfflinePageButtons(typing.NamedTuple):
    back: ttk.Button


class OfflinePage(PageFrame):
    def __init__(self, parent_frame: tk.Frame, page_manager: PageManager) -> None:
        super().__init__(parent_frame)
        buttons: OfflinePageButtons = self.create_buttons(page_manager)
        label: ttk.Label = ttk.Label(self, text="Offline", font=("Verdana", 20))
        label.pack()
        buttons.back.pack()

    def create_buttons(self, page_manager: PageManager) -> OfflinePageButtons:
        back_button: ttk.Button = ttk.Button(
            self, text="Back", command=lambda: page_manager.show_page("StartPage"))
        return OfflinePageButtons(back_button)
