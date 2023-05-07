import tkinter as tk
from launcher.tk.page_frame import PageFrame


class OnlinePage(PageFrame):
    def __init__(self, parent_frame: tk.Frame, launcher: tk.Tk) -> None:
        super().__init__(parent_frame, launcher)
