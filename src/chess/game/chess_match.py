import datetime
import enum

from chess_engine.movement.validate_move import is_checkmate
from chess_engine.movement.validate_move import is_material_insufficient
from chess_engine.movement.validate_move import is_move_valid
from chess_engine.movement.validate_move import is_stale_mate
from chess_engine.movement.validate_move import is_take
from chess_engine.notation.algebraic_notation import AlgebraicNotation
from chess_engine.notation.forsyth_edwards_notation import Fen
from chess_engine.notation.forsyth_edwards_notation import FenChars
from chess_engine.notation.forsyth_edwards_notation import encode_fen_data
from chess_engine.notation.forsyth_edwards_notation import validate_fen_castling_rights
from chess_engine.notation.forsyth_edwards_notation import validate_fen_en_passant_rights
from chess_engine.notation.forsyth_edwards_notation import validate_fen_piece_placement

from chess.board.side import Side
from chess.timer.timer_config import TimerConfig
from config.pg_config import AGREEMENT
from config.pg_config import CHECKMATE
from config.pg_config import FIFTY_MOVE_RULE
from config.pg_config import HALF_MOVE_LIMIT
from config.pg_config import INSUFFICIENT_MATERIAL
from config.pg_config import REPETITION
from config.pg_config import RESIGNATION
from config.pg_config import STALEMATE
from config.pg_config import TIMEOUT
from event.event import EventType
from event.game_events import ContinueGameEvent
from event.game_events import DrawResponseEvent
from event.game_events import EndGameEvent
from event.game_events import GameEvent
from event.game_events import InvalidMoveEvent
from event.game_events import MoveEvent
from event.game_events import OfferDrawEvent
from event.game_events import OpponentDrawOfferEvent
from event.game_events import PromotionEvent
from event.game_events import ResignEvent
from event.game_events import TimeOutEvent
from event.game_events import UpdateCapturedPiecesEvent
from event.game_events import OpponentPromotionEvent
from event.game_events import UpdateFenEvent
from event.local_event_queue import LocalEvents


class MatchResult(enum.Enum):
    WHITE = enum.auto()
    BLACK = enum.auto()
    DRAW = enum.auto()


class RepetitionCounter:
    def __init__(self) -> None:
        self.reached_positions: dict[str, int] = {}
        self.three_fold_repetition: bool = False

    def add_position(self, piece_placement: str, en_passant: str, castling_rights: str) -> None:
        validate_fen_piece_placement(piece_placement)
        validate_fen_en_passant_rights(en_passant)
        validate_fen_castling_rights(castling_rights)
        position = piece_placement + en_passant + castling_rights
        if position not in self.reached_positions:
            self.reached_positions[position] = 1
            return

        if self.reached_positions[position] >= 2:
            self.three_fold_repetition = True
        else:
            self.reached_positions[position] += 1

    def is_three_fold_repetition(self) -> bool:
        return self.three_fold_repetition


class Match:
    def __init__(self, timer_config: TimerConfig):
        self.fen: Fen = Fen()
        self.captured_pieces: str = ''
        self.timer_config = timer_config
        self.prev_time: datetime.datetime | None = None
        self.white_time_left: float = timer_config.time
        self.black_time_left: float = timer_config.time
        self.repetition_counter: RepetitionCounter = RepetitionCounter()

    def process_game_event(self, game_event: GameEvent) -> list[GameEvent]:
        response: list[GameEvent] = []

        if isinstance(game_event, PromotionEvent):
            response.append(OpponentPromotionEvent(-1))

        elif isinstance(game_event, MoveEvent):
            response.extend(self.process_move_event(game_event, Fen(encode_fen_data(self.fen.data))))

        elif isinstance(game_event, ResignEvent):
            response.append(EndGameEvent(-1, Side[game_event.side].get_opposite().name, RESIGNATION))

        elif isinstance(game_event, OfferDrawEvent):
            response.append(OpponentDrawOfferEvent(-1, game_event.side))

        elif isinstance(game_event, DrawResponseEvent):
            if game_event.result:
                response.append(EndGameEvent(-1, MatchResult.DRAW.name, AGREEMENT))
            else:
                response.append(ContinueGameEvent(-1))

        elif isinstance(game_event, TimeOutEvent):
            response.append(EndGameEvent(-1, Side[game_event.side].get_opposite().name, TIMEOUT))

        else:
            assert False, f" {game_event.type.name} : event not recognised"

        response.extend(self.check_for_draws(response))

        return response

    def process_local_move(self) -> None:
        local_events: LocalEvents = LocalEvents.get()
        if (event := local_events.get_match_event()) is None:
            return

        for game_event in self.process_game_event(event):
            local_events.add_player_event(game_event)

    def process_move_event(self, move: MoveEvent, before_move_fen: Fen) -> list[GameEvent]:
        from_index: int = AlgebraicNotation.get_index_from_an(*move.from_)
        dest_index: int = AlgebraicNotation.get_index_from_an(*move.dest)

        if not is_side_valid(move.side, self.fen.is_white_turn()) or \
                not is_move_valid(from_index, dest_index, self.fen):
            return [InvalidMoveEvent(-1)]

        time: datetime.datetime = datetime.datetime.fromisoformat(move.time_iso)
        if self.prev_time is not None:
            diff = time - self.prev_time
            if self.fen.data.active_color == FenChars.WHITE_ACTIVE_COLOR:
                self.white_time_left -= diff.total_seconds()
                self.white_time_left += self.timer_config.increment
            else:
                self.black_time_left -= diff.total_seconds()
                self.black_time_left += self.timer_config.increment

        self.prev_time = time
        self.fen.make_move(from_index, dest_index, move.target_fen)
        self.repetition_counter.add_position(self.fen.data.piece_placement, self.fen.data.en_passant_rights,
                                             self.fen.data.castling_rights)

        response: list[GameEvent] = [UpdateFenEvent(-1, self.fen.notation, self.white_time_left, self.black_time_left,
                                                    from_index, dest_index)]

        is_en_passant: bool = before_move_fen.is_move_en_passant(from_index, dest_index)
        opponent_pawn_fen: str = FenChars.get_piece_fen(FenChars.DEFAULT_PAWN, not before_move_fen.is_white_turn())

        if is_take(before_move_fen, dest_index, is_en_passant, before_move_fen.is_move_castle(from_index, dest_index)):
            if is_en_passant:
                self.captured_pieces += opponent_pawn_fen
            else:
                self.captured_pieces += before_move_fen[dest_index]
            response.append(UpdateCapturedPiecesEvent(-1, self.captured_pieces))

        if is_checkmate(self.fen, self.fen.is_white_turn()):
            result: str = MatchResult.BLACK.name if self.fen.is_white_turn() else MatchResult.WHITE.name
            end_game: EndGameEvent = EndGameEvent(-1, result, CHECKMATE)
            response.append(end_game)

        return response

    def check_for_draws(self, response: list[GameEvent]) -> list[GameEvent]:
        for event in response:
            if event.type is EventType.END_GAME:
                return []

        # Stalemate
        if is_stale_mate(self.fen):
            return [EndGameEvent(-1, MatchResult.DRAW.name, STALEMATE)]

        # Insufficient Material
        if is_material_insufficient(self.fen):
            return [EndGameEvent(-1, MatchResult.DRAW.name, INSUFFICIENT_MATERIAL)]

        # 50 move-rule
        if int(self.fen.data.half_move_clock) >= HALF_MOVE_LIMIT:
            return [EndGameEvent(-1, MatchResult.DRAW.name, FIFTY_MOVE_RULE)]

        # Repetition
        if self.repetition_counter.is_three_fold_repetition():
            return [EndGameEvent(-1, MatchResult.DRAW.name, REPETITION)]

        return []


def is_side_valid(side: str, is_white: bool) -> bool:
    if side == Side.WHITE.name and is_white:
        return True

    if side == Side.BLACK.name and not is_white:
        return True

    return False
