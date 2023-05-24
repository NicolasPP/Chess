import typing
import ttkbootstrap as ttk
from launcher.tk.page.page_manager import PageManager
from launcher.tk.components.tk_component import Component


class NetworkPlayButtons(typing.NamedTuple):
    online: ttk.Button
    offline: ttk.Button
    is_logged_in: ttk.BooleanVar


class NetworkPlayComponent(Component):

    @staticmethod
    def create_play_buttons(page_manger: PageManager, play_frame: ttk.LabelFrame) -> NetworkPlayButtons:
        online_button: ttk.Button = ttk.Button(play_frame, text="Online",
                                               command=lambda: page_manger.show_page("OnlinePage"), state=ttk.DISABLED)
        offline_button: ttk.Button = ttk.Button(play_frame, text="Offline",
                                                command=lambda: page_manger.show_page("OfflinePage"))
        is_logged_in: ttk.BooleanVar = ttk.BooleanVar(value=False)
        is_logged_in.trace_add('write', lambda v, i, m: handle_update_online_button(online_button, is_logged_in))
        return NetworkPlayButtons(online_button, offline_button, is_logged_in)

    def __init__(self, parent: ttk.Frame, page_manager: PageManager) -> None:
        super().__init__(parent, "Play")
        self.play_buttons = NetworkPlayComponent.create_play_buttons(page_manager, self.frame)
        self.play_buttons.online.pack(side=ttk.LEFT, expand=True, anchor=ttk.CENTER)
        self.play_buttons.offline.pack(side=ttk.LEFT, expand=True, anchor=ttk.CENTER)

    def get_play_buttons(self) -> NetworkPlayButtons:
        return self.play_buttons


def handle_update_online_button(online_button: ttk.Button, is_logged_in: ttk.BooleanVar) -> None:
    state = ttk.NORMAL if is_logged_in.get() else ttk.DISABLED
    online_button["state"] = state
