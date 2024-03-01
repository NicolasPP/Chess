from __future__ import annotations

import tkinter as tk
import typing

possible_vars: typing.TypeAlias = tk.StringVar | tk.BooleanVar


class GlobalUserVars:
    global_vars: GlobalUserVars | None = None
    server_disconnect: str = 'server_disconnect'
    connected_users: str = 'connected_users'
    connect_error: str = 'connect_error'
    is_bot_valid: str = 'is_bot_valid'
    launch_game: str = 'launch_game'

    @staticmethod
    def get() -> GlobalUserVars:
        if GlobalUserVars.global_vars is None:
            GlobalUserVars.global_vars = GlobalUserVars()
        return GlobalUserVars.global_vars

    def __init__(self):
        self.vars: dict[str, possible_vars] = {
            GlobalUserVars.server_disconnect: tk.BooleanVar(value=False),
            GlobalUserVars.is_bot_valid: tk.BooleanVar(value=False),
            GlobalUserVars.connect_error: tk.StringVar(),
            GlobalUserVars.launch_game: tk.StringVar()
        }

    def get_var(self, name: str) -> possible_vars:
        var: possible_vars = self.vars.get(name)
        if var is None:
            raise Exception(f"var with name: {name} not found")
        return var
