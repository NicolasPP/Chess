import tkinter as tk


class GlobalUserVars:
    server_disconnect: tk.BooleanVar | None = None
    is_bot_valid: tk.BooleanVar | None = None

    @staticmethod
    def get_server_disconnect() -> tk.BooleanVar:
        if GlobalUserVars.server_disconnect is None:
            GlobalUserVars.server_disconnect = tk.BooleanVar(value=False)
        return GlobalUserVars.server_disconnect

    @staticmethod
    def get_is_bot_valid() -> tk.BooleanVar:
        if GlobalUserVars.is_bot_valid is None:
            GlobalUserVars.is_bot_valid = tk.BooleanVar(value=False)
        return GlobalUserVars.is_bot_valid
