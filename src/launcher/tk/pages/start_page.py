import tkinter as tk
import ttkbootstrap as ttk
from launcher.tk.page_frame import PageFrame


class StartPage(PageFrame):
    def __init__(
            self,
            parent_frame: tk.Frame,
            launcher: tk.Tk,
    ) -> None:
        super().__init__(parent_frame, launcher)

        LARGEFONT = ("Verdana", 35)
        label = ttk.Label(self, text="Startpage", font=LARGEFONT)
        label2 = ttk.Label(self, text="Startpage", font=LARGEFONT)
        label.pack()
        label2.pack()
        button1 = ttk.Button(self, text="Page 1",
                             command=lambda: self.launcher.show_page('SettingsPage'))
        button1.pack()
