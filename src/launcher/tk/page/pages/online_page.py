import tkinter as tk
from ttkbootstrap import ttk
from launcher.tk.page.page_frame import PageFrame
from launcher.tk.page.page_manager import PageManager
from launcher.tk.components.local_server_component import LocalServerComponent
from launcher.tk.components.connect_component import ConnectComponent
from config.tk_config import LAUNCHER_PAD


class OnlinePage(PageFrame):
    def __init__(self, parent_frame: tk.Frame, page_manager: PageManager) -> None:
        super().__init__(parent_frame)
        self.back: ttk.Button = self.create_back_button(page_manager)
        started_server: tk.BooleanVar = tk.BooleanVar(value=False)
        self.connect_comp: ConnectComponent = ConnectComponent(self, page_manager, started_server)
        self.local_server_comp: LocalServerComponent = LocalServerComponent(self, started_server)

        self.grid_rowconfigure(0, weight=10)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=6)
        self.grid_columnconfigure(1, weight=2)

        self.connect_comp.get_frame().grid(row=0, column=0, rowspan=2, sticky=tk.NSEW, padx=LAUNCHER_PAD,
                                           pady=LAUNCHER_PAD)
        self.local_server_comp.get_frame().grid(row=0, column=1, sticky=tk.NSEW, padx=LAUNCHER_PAD, pady=LAUNCHER_PAD)
        self.back.grid(row=1, column=1)

    def create_back_button(self, page_manager: PageManager) -> ttk.Button:
        return ttk.Button(self, text="Back", command=lambda: page_manager.show_page("StartPage"))
