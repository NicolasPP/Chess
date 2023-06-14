import enum


class ServerGameCommand(enum.Enum):
    # commands that the server can send to the client
    UPDATE_FEN = enum.auto()
    END_GAME = enum.auto()
    INVALID_MOVE = enum.auto()
    UPDATE_CAP_PIECES = enum.auto()
    INIT_INFO = enum.auto()
    CLIENT_PROMOTING = enum.auto()
    CLIENT_DRAW_OFFER = enum.auto()
    CONTINUE = enum.auto()


class ServerLauncherCommand(enum.Enum):
    DISCONNECT = enum.auto()
