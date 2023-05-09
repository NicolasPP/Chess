import tkinter as tk
import ttkbootstrap as ttk

from launcher.tk.pages.offline_page import OfflinePage
from launcher.tk.pages.online_page import OnlinePage
from launcher.tk.pages.server_page import ServerPage
from launcher.tk.pages.settings_page import SettingsPage
from launcher.tk.pages.start_page import StartPage
from launcher.tk.page_manager import PageManager
from launcher.pg.pg_launcher import PygameChessLauncher

from config.tk_config import *


class ChessTkinterLauncher(tk.Tk):

    def __init__(self, *args, **kwargs) -> None:
        tk.Tk.__init__(self, *args, **kwargs)
        self.style: ttk.Style = ttk.Style()
        self.pg_launcher: PygameChessLauncher = PygameChessLauncher()

        self.create_styles()
        self.window_innit()

        self.root_frame: ttk.Frame = ttk.Frame(self, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
        self.root_frame.pack(side="top")

        self.page_manager: PageManager = PageManager()
        self.page_manager.add_page(StartPage(self.root_frame, self.page_manager, self.pg_launcher))
        self.page_manager.add_page(OfflinePage(self.root_frame, self.page_manager, self.pg_launcher))
        self.page_manager.add_page(OnlinePage(self.root_frame, self.page_manager, self.pg_launcher))
        self.page_manager.add_page(SettingsPage(self.root_frame, self.page_manager, self.pg_launcher))
        self.page_manager.add_page(ServerPage(self.root_frame, self.page_manager, self.pg_launcher))
        self.page_manager.show_page(StartPage.__name__)

    def create_styles(self) -> None:
        self.style.configure('title.TLabel', background='#343A40', foreground='white')

    def window_innit(self) -> None:
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.title("ChessLauncher")


if __name__ == "__main__":
    root = ChessTkinterLauncher()
    root.mainloop()
