import tkinter as tk

import ttkbootstrap as ttk

from config.tk_config import BG_DARK
from config.tk_config import BG_LIGHT
from config.tk_config import DEFAULT_FONT_SIZE
from config.tk_config import DEFAULT_WINDOW_HEIGHT
from config.tk_config import DEFAULT_WINDOW_WIDTH
from config.tk_config import FG_DARK
from config.tk_config import FG_LIGHT
from config.tk_config import FONT_NAME
from config.tk_config import FRAME_FONT_SIZE
from database.chess_db import ChessDataBase
from database.chess_db import DataBaseInfo
from launcher.pg.pg_launcher import ChessPygameLauncher
from launcher.tk.page.page_manager import PageManager
from launcher.tk.page.pages.offline_page import OfflinePage
from launcher.tk.page.pages.online_page import OnlinePage
from launcher.tk.page.pages.server_page import ServerPage
from launcher.tk.page.pages.start_page import StartPage


class ChessTkinterLauncher(tk.Tk):

    def __init__(self, database_info: DataBaseInfo, *args, **kwargs) -> None:
        tk.Tk.__init__(self, *args, **kwargs)
        self.style: ttk.Style = ttk.Style()
        ChessPygameLauncher.get().set_hide_app(self.withdraw)
        ChessPygameLauncher.get().set_show_app(self.deiconify)
        self.database: ChessDataBase = ChessDataBase(database_info)

        self.window_innit()
        self.create_styles()

        self.root_frame: ttk.Frame = ttk.Frame(self, width=DEFAULT_WINDOW_WIDTH, height=DEFAULT_WINDOW_HEIGHT)
        self.root_frame.pack(fill=ttk.BOTH, expand=True)

        self.page_manager: PageManager = PageManager()
        self.page_manager.add_page(StartPage(self.root_frame, self.page_manager, self.database))
        self.page_manager.add_page(OfflinePage(self.root_frame, self.page_manager))
        self.page_manager.add_page(OnlinePage(self.root_frame, self.page_manager))
        self.page_manager.add_page(ServerPage(self.root_frame, self.page_manager))
        self.page_manager.show_page(StartPage.__name__)

        self.protocol("WM_DELETE_WINDOW", self.exit)

    def exit(self) -> None:
        self.page_manager.get_page(ServerPage.__name__).handle_exit()
        self.quit()

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
        self.style.map('TLabel', foreground=[(tk.DISABLED, BG_LIGHT)])
        self.style.configure('TEntry', fieldbackground=BG_DARK, font=(FONT_NAME, DEFAULT_FONT_SIZE), foreground=FG_DARK,
                             darkcolor=BG_DARK, lightcolor=BG_DARK, bordercolor=FG_DARK, selectbackground=BG_LIGHT,
                             selectforeground=FG_LIGHT)
        self.style.configure('Toolbutton', background=BG_DARK, foreground=FG_DARK, relief=tk.SOLID,
                             font=(FONT_NAME, DEFAULT_FONT_SIZE))
        self.style.map('Toolbutton', background=[(tk.DISABLED, BG_LIGHT), ('selected', BG_DARK)],
                       foreground=[('!selected', BG_LIGHT), (tk.DISABLED, BG_LIGHT)])

    def window_innit(self) -> None:
        self.geometry(f"{DEFAULT_WINDOW_WIDTH}x{DEFAULT_WINDOW_HEIGHT}")
        self.title("ChessLauncher")
        self.minsize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
