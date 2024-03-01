import time

from ttkbootstrap import ttk

from launcher.tk.components.tk_component import Component
from launcher.tk.launcher_user import LauncherUser


class ServerLobbyComponent(Component):
    def __init__(self, parent: ttk.Frame) -> None:
        super().__init__(parent, "Lobby")

        queue: ttk.Button = ttk.Button(self.frame, text="Queue for Match", command=enter_queue)
        queue.pack()


def enter_queue() -> None:
    LauncherUser.get_client().send_queue_request()
