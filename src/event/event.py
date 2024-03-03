from __future__ import annotations

from abc import ABC
from enum import Enum
from enum import auto


class EventType(Enum):
    # commands that the client can send to the server during game
    MOVE = auto()
    PROMOTION = auto()
    RESIGN = auto()
    OFFER_DRAW = auto()
    DRAW_RESPONSE = auto()
    TIME_OUT = auto()

    # commands that the server can send to the client while in game
    UPDATE_FEN = auto()
    END_GAME = auto()
    INVALID_MOVE = auto()
    UPDATE_CAP_PIECES = auto()
    GAME_INIT = auto()
    OPPONENT_PROMOTION = auto()
    OPPONENT_DRAW_OFFER = auto()
    CONTINUE_GAME = auto()

    # commands that the server can send to the client while in the launcher
    DISCONNECT = auto()
    LAUNCH_GAME = auto()

    # commands that the client can send to the server while in the launcher
    SERVER_VERIFICATION = auto()
    ENTER_QUEUE = auto()


class EventContext(Enum):
    GAME = auto()
    LAUNCHER = auto()


class Event(ABC):

    def __init__(self, event_type: EventType, event_context: EventContext) -> None:
        self.type: EventType = event_type
        self.context: EventContext = event_context
