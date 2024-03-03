from event.event import Event
from event.event import EventContext
from event.event import EventType


class GameEvent(Event):
    def __init__(self, event_type: EventType, match_id: int):
        super().__init__(event_type, EventContext.GAME)
        self.match_id: int = match_id


# -- Events sent from the Client to the Server --

class OfferDrawEvent(GameEvent):

    def __init__(self, match_id: int, side: str) -> None:
        super().__init__(EventType.OFFER_DRAW, match_id)
        self.side: str = side


class PromotionEvent(GameEvent):

    def __init__(self, match_id: int) -> None:
        super().__init__(EventType.PROMOTION, match_id)


class ResignEvent(GameEvent):

    def __init__(self, match_id: int, side: str) -> None:
        super().__init__(EventType.RESIGN, match_id)
        self.side: str = side


class TimeOutEvent(GameEvent):

    def __init__(self, match_id: int, side: str) -> None:
        super().__init__(EventType.TIME_OUT, match_id)
        self.side: str = side


class DrawResponseEvent(GameEvent):

    def __init__(self, match_id: int, result: bool) -> None:
        super().__init__(EventType.DRAW_RESPONSE, match_id)
        self.result: bool = result


class MoveEvent(GameEvent):

    def __init__(self, match_id: int, from_: tuple[str, str], dest: tuple[str, str], side: str, target_fen: str,
                 time_iso: str) -> None:
        super().__init__(EventType.MOVE, match_id)
        self.from_: tuple[str, str] = from_
        self.dest: tuple[str, str] = dest
        self.side: str = side
        self.target_fen: str = target_fen
        self.time_iso: str = time_iso


# -- Events sent from the Server to the Client --

class OpponentDrawOfferEvent(GameEvent):

    def __init__(self, match_id: int, side: str) -> None:
        super().__init__(EventType.OPPONENT_DRAW_OFFER, match_id)
        self.side: str = side


class OpponentPromotionEvent(GameEvent):

    def __init__(self, match_id: int) -> None:
        super().__init__(EventType.OPPONENT_PROMOTION, match_id)


class UpdateCapturedPiecesEvent(GameEvent):

    def __init__(self, match_id: int, captured_pieces: str) -> None:
        super().__init__(EventType.UPDATE_CAP_PIECES, match_id)
        self.captured_pieces: str = captured_pieces


class UpdateFenEvent(GameEvent):

    def __init__(self, match_id: int, fen_notation: str, white_time: float, black_time: float, from_: int,
                 dest: int) -> None:
        super().__init__(EventType.UPDATE_FEN, match_id)
        self.notation: str = fen_notation
        self.white_time: float = white_time
        self.black_time: float = black_time
        self.from_: int = from_
        self.dest: int = dest


class ContinueGameEvent(GameEvent):

    def __init__(self, match_id: int) -> None:
        super().__init__(EventType.CONTINUE_GAME, match_id)


class EndGameEvent(GameEvent):

    def __init__(self, match_id: int, result: str, reason: str) -> None:
        super().__init__(EventType.END_GAME, match_id)
        self.result: str = result
        self.reason: str = reason


class InvalidMoveEvent(GameEvent):

    def __init__(self, match_id: int) -> None:
        super().__init__(EventType.INVALID_MOVE, match_id)
