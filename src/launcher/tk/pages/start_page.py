import typing
import tkinter as tk
import ttkbootstrap as ttk
from launcher.tk.page_frame import PageFrame
from launcher.tk.page_manager import PageManager


class StartPageButtons(typing.NamedTuple):
    settings: ttk.Button
    online: ttk.Button
    offline: ttk.Button


class StartPage(PageFrame):

    def __init__(
            self,
            parent_frame: tk.Frame,
            page_manager: PageManager,
    ) -> None:
        super().__init__(parent_frame)
        buttons = self.create_buttons(page_manager)
        label = ttk.Label(self, text="Startpage", font=("Verdana", 20))
        label.pack(expand=True)
        buttons.online.pack(expand=True)
        buttons.offline.pack(expand=True)
        buttons.settings.pack(expand=True)

    def create_buttons(self, page_manger: PageManager) -> StartPageButtons:
        settings_buttons: ttk.Button = ttk.Button(
            self, text="Settings", command=lambda: page_manger.show_page("SettingsPage"))
        online_button: ttk.Button = ttk.Button(
            self, text="Online", command=lambda: page_manger.show_page("OnlinePage"))
        offline_button: ttk.Button = ttk.Button(
            self, text="Offline", command=lambda: page_manger.show_page("OfflinePage"))
        return StartPageButtons(settings_buttons, online_button, offline_button)
