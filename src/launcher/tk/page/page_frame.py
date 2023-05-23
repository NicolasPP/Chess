import ttkbootstrap as ttk


class PageFrame(ttk.Frame):
    def __init__(self, parent_frame: ttk.Frame) -> None:
        ttk.Frame.__init__(self, parent_frame)
        self["width"], self["height"] = parent_frame["width"], parent_frame["height"]
        self.parent_frame: ttk.Frame = parent_frame