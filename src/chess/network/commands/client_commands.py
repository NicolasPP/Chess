import enum


class ClientCommand(enum.Enum):
    # commands that the client can send to the server
    MOVE = enum.auto()
    PICKING_PROMOTION = enum.auto()
    RESIGN = enum.auto()
    OFFER_DRAW = enum.auto()
    DRAW_RESPONSE = enum.auto()
    TIME_OUT = enum.auto()
