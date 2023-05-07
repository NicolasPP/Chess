import tkinter as tk
import ttkbootstrap as ttk
from launcher.tk.page_frame import PageFrame


class SettingsPage(PageFrame):
    def __init__(self, parent_frame: tk.Frame, launcher: tk.Tk) -> None:
        super().__init__(parent_frame, launcher)
        LARGEFONT = ("Verdana", 35)
        label = ttk.Label(self, text="Settings", font=LARGEFONT)
        label.pack()
        button1 = ttk.Button(self, text="Page 1",
                             command=lambda: launcher.show_page('StartPage'))
        button1.pack()
