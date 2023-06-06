from ttkbootstrap import ttk


class PageFrame(ttk.Frame):
    def __init__(self, parent_frame: ttk.Frame) -> None:
        ttk.Frame.__init__(self, parent_frame)
        self.configure(width=parent_frame["width"], height=parent_frame["height"])
        self.parent_frame: ttk.Frame = parent_frame
