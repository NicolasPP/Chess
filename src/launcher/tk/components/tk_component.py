import ttkbootstrap as ttk


class Component:

    def __init__(self, parent: ttk.Frame, text: str) -> None:
        self.frame: ttk.LabelFrame = ttk.LabelFrame(parent, text=text)

    def get_frame(self) -> ttk.LabelFrame:
        return self.frame
