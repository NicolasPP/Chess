import tkinter as tk
import ttkbootstrap as ttk

from launcher.tk.pages.offline_page import OfflinePage
from launcher.tk.pages.online_page import OnlinePage
from launcher.tk.pages.server_page import ServerPage
from launcher.tk.pages.start_page import StartPage
from launcher.tk.page_manager import PageManager
from launcher.pg.pg_launcher import PygameChessLauncher

from config.tk_config import *


class ChessTkinterLauncher(tk.Tk):

    def __init__(self, *args, **kwargs) -> None:
        tk.Tk.__init__(self, *args, **kwargs)
        self.style: ttk.Style = ttk.Style()
        self.pg_launcher: PygameChessLauncher = PygameChessLauncher(self.deiconify, self.withdraw)

        self.window_innit()
        self.create_styles()

        self.root_frame: ttk.Frame = ttk.Frame(self, width=DEFAULT_WINDOW_WIDTH, height=DEFAULT_WINDOW_HEIGHT)
        self.root_frame.pack(fill=ttk.BOTH, expand=True)

        is_bot_valid: ttk.BooleanVar = ttk.BooleanVar(value=False)

        self.page_manager: PageManager = PageManager()
        self.page_manager.add_page(StartPage(self.root_frame, self.page_manager, is_bot_valid, self.pg_launcher))
        self.page_manager.add_page(OfflinePage(self.root_frame, self.page_manager, self.pg_launcher, is_bot_valid))
        self.page_manager.add_page(OnlinePage(self.root_frame, self.page_manager, self.pg_launcher))
        self.page_manager.add_page(ServerPage(self.root_frame, self.page_manager, self.pg_launcher))
        self.page_manager.show_page(StartPage.__name__)

    def create_styles(self) -> None:
        self.style.configure('title.TLabel', background=BG_DARK, foreground=FG_LIGHT)
        self.style.configure('TFrame', background=BG_DARK)
        self.style.configure('TLabelframe', background=BG_DARK, bordercolor=FG_LIGHT, anchor=ttk.CENTER,
                             relief=ttk.SOLID)
        self.style.configure('TLabelframe.Label', foreground=FG_DARK, background=BG_DARK, font=(FONT_NAME,
                                                                                                FRAME_FONT_SIZE))
        self.style.configure('TButton', foreground=FG_DARK, background=BG_DARK, focuscolor=FG_DARK,
                             bordercolor=FG_LIGHT, relief=ttk.FLAT, anchor=ttk.CENTER,
                             font=(FONT_NAME, DEFAULT_FONT_SIZE), focusthickness=5)
        self.style.map('TButton', background=[(ttk.ACTIVE, BG_LIGHT)])
        self.style.configure('TMenubutton', background=BG_DARK, foreground=FG_DARK, font=(FONT_NAME, DEFAULT_FONT_SIZE),
                             arrowcolor=FG_LIGHT, bordercolor=BG_LIGHT, relief=ttk.SOLID)
        self.style.configure('TScale', background=BG_DARK)
        self.style.configure('TLabel', background=BG_DARK, font=(FONT_NAME, DEFAULT_FONT_SIZE), foreground=FG_DARK)
        self.style.configure('TEntry', fieldbackground=BG_DARK, font=(FONT_NAME, DEFAULT_FONT_SIZE), foreground=FG_DARK,
                             darkcolor=BG_DARK, lightcolor=BG_DARK, bordercolor=FG_DARK, selectbackground=BG_DARK,
                             selectforeground=BG_DARK)

    def window_innit(self) -> None:
        self.geometry(f"{DEFAULT_WINDOW_WIDTH}x{DEFAULT_WINDOW_HEIGHT}")
        self.title("ChessLauncher")
        self.minsize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)


if __name__ == "__main__":
    root = ChessTkinterLauncher()
    root.mainloop()
