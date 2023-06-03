import tkinter as tk


class GlobalUserVars:
    server_disconnect: tk.BooleanVar | None = None

    @staticmethod
    def get_server_disconnect() -> tk.BooleanVar:
        if GlobalUserVars.server_disconnect is None:
            GlobalUserVars.server_disconnect = tk.BooleanVar(value=False)
        return GlobalUserVars.server_disconnect
