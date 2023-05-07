import tkinter as tk


class PageFrame(tk.Frame):
    def __init__(self, parent_frame: tk.Frame, launcher: tk.Tk) -> None:
        tk.Frame.__init__(self, parent_frame)
        self.parent_frame: tk.Frame = parent_frame
        self.launcher: tk.Tk = launcher
        self.grid(column=0, row=0, sticky='nsew')
