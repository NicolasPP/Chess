from ttkbootstrap import ttk


class Component:

    @staticmethod
    def get_title(title: str) -> str:
        return f" {title.strip()} "

    def __init__(self, parent: ttk.Frame, title: str) -> None:
        self.frame: ttk.LabelFrame = ttk.LabelFrame(parent)
        self.set_title(title)

    def get_frame(self) -> ttk.LabelFrame:
        return self.frame

    def set_title(self, title) -> None:
        self.frame["text"] = Component.get_title(title)
