import enum


class ClientGameCommand(enum.Enum):
    # commands that the client can send to the server during game
    MOVE = enum.auto()
    PICKING_PROMOTION = enum.auto()
    RESIGN = enum.auto()
    OFFER_DRAW = enum.auto()
    DRAW_RESPONSE = enum.auto()
    TIME_OUT = enum.auto()


class ClientLauncherCommand(enum.Enum):
    VERIFICATION = enum.auto()
    ENTER_QUEUE = enum.auto()
