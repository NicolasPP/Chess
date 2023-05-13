import typing
import tkinter as tk
import ttkbootstrap as ttk
from launcher.tk.page_frame import PageFrame
from launcher.tk.page_manager import PageManager
from launcher.pg.pg_launcher import PygameChessLauncher


class StartPageButtons(typing.NamedTuple):
    online: ttk.Button
    offline: ttk.Button


class StartPage(PageFrame):

    @staticmethod
    def create_buttons(page_manger: PageManager, play_frame: ttk.LabelFrame) -> StartPageButtons:
        online_button: ttk.Button = ttk.Button(play_frame, text="Online",
                                               command=lambda: page_manger.show_page("OnlinePage"))
        offline_button: ttk.Button = ttk.Button(play_frame, text="Offline",
                                                command=lambda: page_manger.show_page("OfflinePage"))
        return StartPageButtons(online_button, offline_button)

    def __init__(self, parent_frame: tk.Frame, page_manager: PageManager, pg_launcher: PygameChessLauncher) -> None:
        super().__init__(parent_frame)
        play_frame: ttk.LabelFrame = ttk.LabelFrame(self, text='Play')
        settings_frame: ttk.LabelFrame = ttk.LabelFrame(self, text='Settings')
        user_frame: ttk.LabelFrame = ttk.LabelFrame(self, text='User')

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=3)
        self.rowconfigure(1, weight=7)

        buttons = StartPage.create_buttons(page_manager, play_frame)
        play_frame.grid(row=0, column=0, sticky="news", padx=5, pady=5)
        buttons.online.pack(side="left", expand=True)
        buttons.offline.pack(side="left", expand=True)

        buttons1 = StartPage.create_buttons(page_manager, settings_frame)
        settings_frame.grid(row=0, column=1, rowspan=2, sticky="news", padx=5, pady=5)
        buttons1.online.pack(side="top", expand=True)
        buttons1.offline.pack(side="top", expand=True)

        buttons2 = StartPage.create_buttons(page_manager, user_frame)
        user_frame.grid(row=1, column=0, sticky="news", padx=5, pady=5)
        buttons2.online.pack(side="top", expand=True)
        buttons2.offline.pack(side="top", expand=True)
