from ttkbootstrap import ttk
from launcher.tk.components.tk_component import Component


class BotConfigComponent(Component):
    def __init__(self, parent: ttk.Frame) -> None:
        super().__init__(parent, "Bot Settings")
