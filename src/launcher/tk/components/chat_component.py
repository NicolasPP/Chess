from ttkbootstrap import ttk

from launcher.tk.components.tk_component import Component


class ChatComponent(Component):
    def __init__(self, parent: ttk.Frame) -> None:
        super().__init__(parent, "Chat")
