import tkinter as tk

from launcher.tk.page_frame import PageFrame
from launcher.tk.pages.offline_page import OfflinePage
from launcher.tk.pages.online_page import OnlinePage
from launcher.tk.pages.server_page import ServerPage
from launcher.tk.pages.settings_page import SettingsPage
from launcher.tk.pages.start_page import StartPage


class PageManager:
    def __init__(self) -> None:
        self.pages: dict[str, PageFrame] = {}

    def add_page(self, page_frame: PageFrame) -> None:
        self.pages[type(page_frame).__name__] = page_frame

    def get_page(self, page_name: str) -> PageFrame:
        page_frame = self.pages.get(page_name)
        if page_frame is None:
            raise Exception(f'page name: {page_name} is not a valid id')
        return page_frame


class ChessTkinterLauncher(tk.Tk):

    def __init__(self, *args, **kwargs) -> None:
        tk.Tk.__init__(self, *args, **kwargs)
        self.root_frame: tk.Frame = tk.Frame(self, height=100, width=150, bg="Red")
        self.root_frame.pack(side="top", fill="none")
        self.page_manager: PageManager = PageManager()
        self.page_manager.add_page(StartPage(self.root_frame, self))
        self.page_manager.add_page(OfflinePage(self.root_frame, self))
        self.page_manager.add_page(OnlinePage(self.root_frame, self))
        self.page_manager.add_page(SettingsPage(self.root_frame, self))
        self.page_manager.add_page(ServerPage(self.root_frame, self))
        self.show_page(StartPage.__name__)

    def show_page(self, page_name: str) -> None:
        self.page_manager.get_page(page_name).tkraise()


if __name__ == "__main__":
    ChessTkinterLauncher().mainloop()
