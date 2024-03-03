from __future__ import annotations

import datetime
import enum
import socket
from collections import deque
from typing import Callable
from typing import Optional

import pygame
from chess_engine.movement.piece_movement import is_pawn_promotion
from chess_engine.notation.forsyth_edwards_notation import Fen
from chess_engine.notation.forsyth_edwards_notation import FenChars

from chess.asset.asset_manager import AssetManager
from chess.board.board_tile import BoardTile
from chess.board.chess_board import Board
from chess.board.side import Side
from chess.game.chess_match import Match
from chess.game.game_size import GameSize
from chess.game.game_surface import GameSurface
from config.pg_config import DRAW_DOUBLE_CHECK_LABEL
from config.pg_config import MOUSECLICK_LEFT
from config.pg_config import MOUSECLICK_SCROLL_DOWN
from config.pg_config import MOUSECLICK_SCROLL_UP
from config.pg_config import RESIGN_DOUBLE_CHECK_LABEL
from config.pg_config import RESPOND_DRAW_LABEL
from config.pg_config import Y_AXIS_WIDTH
from event.event_manager import EventManager
from event.game_events import ContinueGameEvent
from event.game_events import DrawResponseEvent
from event.game_events import EndGameEvent
from event.game_events import GameEvent
from event.game_events import InvalidMoveEvent
from event.game_events import MoveEvent
from event.game_events import OfferDrawEvent
from event.game_events import OpponentDrawOfferEvent
from event.game_events import OpponentPromotionEvent
from event.game_events import PromotionEvent
from event.game_events import ResignEvent
from event.game_events import TimeOutEvent
from event.game_events import UpdateCapturedPiecesEvent
from event.game_events import UpdateFenEvent
from event.local_event_queue import LocalEvents
from gui.available_moves_gui import AvailableMovesGui
from gui.board_axis_gui import BoardAxisGui
from gui.captured_gui import CapturedGui
from gui.end_game_gui import EndGameGui
from gui.played_moves_gui import PlayedMovesGui
from gui.previous_move_gui import PreviousMoveGui
from gui.promotion_gui import PromotionGui
from gui.timer_gui import TimerGui
from gui.timer_gui import TimerRects
from gui.verify_gui import VerifyGui


class State(enum.Enum):
    PICK_PIECE = enum.auto()
    DROP_PIECE = enum.auto()
    PICKING_PROMOTION = enum.auto()
    OFFERED_DRAW = enum.auto()
    RESPOND_DRAW = enum.auto()
    DRAW_DOUBLE_CHECK = enum.auto()
    RESIGN_DOUBLE_CHECK = enum.auto()


class Player:
    @staticmethod
    def get_player_local(side: Side, match: Match, game_offset: pygame.rect.Rect) -> Player:
        player = Player(side, match.timer_config.time, game_offset)
        player.update_turn(match.fen)
        player.update_pieces_location(match.fen)
        return player

    def __init__(self, side: Side, time_left: float, game_offset: pygame.rect.Rect):

        self.game_offset: pygame.rect.Rect = game_offset
        self.board: Board = Board(side)
        self.set_to_default_pos()
        self.side: Side = side
        self.state: State = State.PICK_PIECE
        self.prev_left_mouse_up: tuple[int, int] = 0, 0
        self.prev_time_iso: str | None = None
        self.turn: bool = side is Side.WHITE
        self.is_render_required: bool = True
        self.game_over: bool = False
        self.read_input: bool = True
        self.opponent_promoting: bool = False
        self.timed_out: bool = False
        self.final_render: bool = True
        self.match_id: Optional[int] = None

        self.promotion_gui: PromotionGui = PromotionGui(self.side, self.board.get_rect())
        self.captured_gui: CapturedGui = CapturedGui('', self.board.get_rect())
        self.timer_gui: TimerGui = TimerGui(time_left, self.board.get_rect())
        self.end_game_gui: EndGameGui = EndGameGui(self.board.get_rect())
        self.verify_gui: VerifyGui = VerifyGui(self.board.get_rect())
        self.axis_gui: BoardAxisGui = BoardAxisGui(self.board.get_rect(), self.side)
        self.available_moves_gui: AvailableMovesGui = AvailableMovesGui()
        self.previous_move_gui: PreviousMoveGui = PreviousMoveGui(self.board.rect)
        self.played_moves_gui: PlayedMovesGui = PlayedMovesGui(self.board.rect)

    def set_match_id(self, match_id: int) -> None:
        self.match_id = match_id

    def get_match_id(self) -> int:
        return -1 if self.match_id is None else self.match_id

    def parse_input(self, event: pygame.event.Event, fen: Fen, connection: Optional[socket.socket] = None) -> None:
        if self.game_over:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == MOUSECLICK_LEFT:
                    if self.end_game_gui.game_over_gui.is_quit_collision(self.game_offset):
                        pygame.quit()
            return

        if not self.read_input:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == MOUSECLICK_SCROLL_UP:
                self.played_moves_gui.scroll_up(self.game_offset)
            if event.button == MOUSECLICK_SCROLL_DOWN:
                self.played_moves_gui.scroll_down(self.game_offset)
            if event.button == MOUSECLICK_LEFT:
                self.handle_mouse_down_left(connection)
                self.handle_end_game_mouse_down()
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == MOUSECLICK_LEFT:
                self.handle_mouse_up_left(connection, fen)

    def handle_end_game_mouse_down(self) -> None:
        if any([self.state == State.RESPOND_DRAW, self.state == State.OFFERED_DRAW,
                self.state == State.RESIGN_DOUBLE_CHECK, self.state == State.DRAW_DOUBLE_CHECK]):
            return

        mouse_pos = pygame.math.Vector2(pygame.mouse.get_pos()) - pygame.math.Vector2(self.game_offset.topleft)
        if self.end_game_gui.offer_draw.rect.collidepoint(mouse_pos.x,
                                                          mouse_pos.y) and self.end_game_gui.offer_draw.enabled:
            self.state = State.DRAW_DOUBLE_CHECK
            self.verify_gui.set_action_label(DRAW_DOUBLE_CHECK_LABEL)
            self.end_game_gui.offer_draw.set_hover(False)
            self.end_game_gui.resign.set_hover(False)

        elif self.end_game_gui.resign.rect.collidepoint(mouse_pos.x, mouse_pos.y) and self.end_game_gui.resign.enabled:
            self.state = State.RESIGN_DOUBLE_CHECK
            self.verify_gui.set_action_label(RESIGN_DOUBLE_CHECK_LABEL)
            self.end_game_gui.offer_draw.set_hover(False)
            self.end_game_gui.resign.set_hover(False)

    def handle_mouse_up_left(self, connection: Optional[socket.socket], fen: Fen) -> None:
        if self.state is not State.DROP_PIECE:
            return

        self.end_game_gui.offer_draw.set_hover(True)
        self.end_game_gui.resign.set_hover(True)

        from_tile: BoardTile = self.board.get_picked_up()
        dest_tile: BoardTile | None = self.board.get_collided_tile(self.game_offset)
        is_promotion: bool = False

        from_coordinates: tuple[str, str] = from_tile.algebraic_notation.file, from_tile.algebraic_notation.rank
        time_iso: str = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Defining the base move as invalid
        move_event: MoveEvent = MoveEvent(self.get_match_id(), from_coordinates, from_coordinates, self.side.name,
                                          from_tile.fen_val, time_iso)

        if dest_tile:
            is_promotion: bool = is_pawn_promotion(from_tile.algebraic_notation, dest_tile.algebraic_notation, fen)
            move_event.dest = dest_tile.algebraic_notation.file, dest_tile.algebraic_notation.rank

        if not is_promotion:
            dispatch_event(connection, move_event)
            self.set_read_input(False)
            self.state = State.PICK_PIECE
            self.board.reset_picked_up()

        else:
            self.state = State.PICKING_PROMOTION
            if connection is not None:
                dispatch_event(connection, PromotionEvent(self.get_match_id()))

        self.prev_left_mouse_up = pygame.mouse.get_pos()
        self.prev_time_iso = time_iso

    def handle_mouse_down_left(self, connection: Optional[socket.socket]) -> None:
        if self.state is State.DROP_PIECE:
            return

        if self.state is State.PICKING_PROMOTION:
            self.handle_pick_promotion(connection)

        elif self.state is State.PICK_PIECE:
            tile = self.board.get_collided_tile(self.game_offset)
            if not tile:
                return

            if tile.fen_val == FenChars.BLANK_PIECE:
                return

            self.board.set_picked_up(tile)
            self.state = State.DROP_PIECE
            self.end_game_gui.offer_draw.set_hover(False)
            self.end_game_gui.resign.set_hover(False)

        elif self.state is State.RESPOND_DRAW:
            self.verify_gui.handle_response(self.game_offset)
            if self.verify_gui.result is None:
                return

            dispatch_event(connection, DrawResponseEvent(self.get_match_id(), self.verify_gui.result))
            self.verify_gui.set_result(None)

        elif self.state is State.DRAW_DOUBLE_CHECK or self.state is State.RESIGN_DOUBLE_CHECK:
            self.verify_gui.handle_response(self.game_offset)
            if self.verify_gui.result is None:
                return

            if not self.verify_gui.result:
                self.state = State.PICK_PIECE
                self.set_require_render(True)
                self.end_game_gui.resign.set_hover(True)
                self.end_game_gui.offer_draw.set_hover(True)
                return

            if self.state is State.DRAW_DOUBLE_CHECK:
                self.state = State.OFFERED_DRAW
                dispatch_event(connection, OfferDrawEvent(self.get_match_id(), self.side.name))
            else:
                dispatch_event(connection, ResignEvent(self.get_match_id(), self.side.name))

            self.verify_gui.set_result(None)
            self.set_require_render(True)

    def handle_pick_promotion(self, connection: Optional[socket.socket]) -> None:
        if self.prev_time_iso is None:
            return

        for surface, rect, val in self.promotion_gui.promotion_pieces:
            mouse_pos = pygame.math.Vector2(pygame.mouse.get_pos()) - pygame.math.Vector2(self.game_offset.topleft)
            if not rect.collidepoint(mouse_pos.x, mouse_pos.y):
                continue

            if (dest_tile := self.board.get_collided_tile(self.game_offset, self.prev_left_mouse_up)) is None:
                continue

            if (from_tile := self.board.get_picked_up()) is None:
                continue

            from_coordinates: tuple[str, str] = from_tile.algebraic_notation.file, from_tile.algebraic_notation.rank
            dest_coordinates: tuple[str, str] = dest_tile.algebraic_notation.file, dest_tile.algebraic_notation.rank

            move_event: MoveEvent = MoveEvent(self.get_match_id(), from_coordinates, dest_coordinates, self.side.name,
                                              val, self.prev_time_iso)

            dispatch_event(connection, move_event)
            self.board.reset_picked_up()
            self.state = State.PICK_PIECE
            self.set_require_render(True)

    def update(self, delta_time: float, connection: Optional[socket.socket] = None) -> None:
        if any([self.game_over, self.opponent_promoting, self.timed_out, self.state == State.PICKING_PROMOTION,
                self.state == State.OFFERED_DRAW, self.state == State.RESPOND_DRAW]):
            return

        if self.state != State.DRAW_DOUBLE_CHECK and self.state != State.RESIGN_DOUBLE_CHECK:
            self.axis_gui.update_hover_highlight(self.board.get_collided_tile(self.game_offset))

        self.timer_gui.tick(delta_time)
        if self.timer_gui.own_timer.time_left <= 0:
            dispatch_event(connection, TimeOutEvent(self.get_match_id(), self.side.name))
            self.set_timed_out(True)

    def handle_draw_offer(self, side: str) -> None:
        self.end_game_gui.offer_draw.set_hover(False)
        self.end_game_gui.resign.set_hover(False)
        if self.side.name != side:
            self.state = State.RESPOND_DRAW
            self.verify_gui.set_action_label('')
            self.verify_gui.set_description_label(RESPOND_DRAW_LABEL)

    def continue_game(self) -> None:
        self.end_game_gui.offer_draw.set_hover(True)
        self.end_game_gui.resign.set_hover(True)
        self.state = State.PICK_PIECE

    def render(self) -> None:
        if self.game_over:
            if not pygame.get_init():
                return
            self.end_game_gui.game_over_gui.quit_button.render(self.game_offset)
            return

        self.timer_gui.render()
        self.axis_gui.render()
        self.played_moves_gui.render()
        self.end_game_gui.render(self.game_offset)

        if self.is_render_required or self.state is State.DROP_PIECE:
            GameSurface.get().fill(AssetManager.get_theme().primary_dark)
            self.timer_gui.render()
            self.end_game_gui.render(self.game_offset)
            self.captured_gui.render(self.side)
            self.board.render()
            self.axis_gui.render()
            self.played_moves_gui.render()
            self.previous_move_gui.render()
            self.board.render_pieces(self.side is Side.WHITE)
            if self.state is State.DROP_PIECE:
                picked: BoardTile = self.board.get_picked_up()
                self.available_moves_gui.render(picked, self.board, self.side, self.turn)
                picked.render(self.game_offset.topleft)

        if self.state is State.PICKING_PROMOTION:
            self.promotion_gui.render()

        if self.state is State.RESPOND_DRAW or \
                self.state is State.DRAW_DOUBLE_CHECK or \
                self.state is State.RESIGN_DOUBLE_CHECK:
            self.verify_gui.render(self.game_offset)

        self.set_require_render(False)

    def update_pieces_location(self, fen: Fen) -> None:
        for index, fen_val in enumerate(fen.expanded):
            tile = self.board.grid[index]
            tile.fen_val = fen_val
            self.available_moves_gui.update_available_moves(fen, self.side, index)
        self.set_require_render(True)

    def end_game(self, game_result: str, result_type: str) -> None:
        self.state = State.PICK_PIECE
        self.set_require_render(True)
        if self.final_render:
            self.render()
        self.set_turn(False)
        self.set_game_over(True)
        self.end_game_gui.game_over_gui.set_final_frame(game_result, result_type)
        if self.final_render:
            self.end_game_gui.game_over_gui.render(self.game_offset)

    def update_turn(self, fen: Fen) -> None:
        if self.side is Side.WHITE:
            if fen.is_white_turn():
                self.set_turn(True)
            else:
                self.set_turn(False)
        else:
            if not fen.is_white_turn():
                self.set_turn(True)
            else:
                self.set_turn(False)

    def set_final_render(self, final_render: bool) -> None:
        self.final_render = final_render

    def set_require_render(self, is_render_required: bool) -> None:
        self.is_render_required = is_render_required

    def set_game_over(self, game_over: bool) -> None:
        self.game_over = game_over

    def set_turn(self, turn: bool) -> None:
        self.turn = turn

    def set_timed_out(self, timed_out: bool) -> None:
        self.timed_out = timed_out

    def set_to_default_pos(self) -> None:
        timer_rects: TimerRects = TimerGui.calculate_timer_rects()
        self.board.get_rect().topleft = (
            int(Y_AXIS_WIDTH * GameSize.get_scale()), int(timer_rects.spacing.height + timer_rects.timer.height))

    def set_read_input(self, read_input: bool) -> None:
        self.read_input = read_input

    def set_opponent_promoting(self, promoting: bool) -> None:
        self.opponent_promoting = promoting

    @staticmethod
    def process_game_event(game_event: GameEvent, fen: Fen, *players: Player) -> None:
        def exec_player(func: Callable[[Player], None]) -> None:
            deque(map(func, players))

        def process_update_fen(update_fen: UpdateFenEvent) -> None:
            pre_move_fen: Fen = Fen(fen.notation)
            fen.notation = update_fen.notation

            exec_player(lambda player: player.update_pieces_location(fen))
            exec_player(lambda player: player.update_turn(fen))
            exec_player(
                lambda player: player.timer_gui.update(player.side, fen.data.active_color, update_fen.white_time,
                                                       update_fen.black_time))
            exec_player(lambda player: player.set_read_input(True))
            exec_player(lambda player: player.set_opponent_promoting(False))
            exec_player(lambda player: player.previous_move_gui.set_prev_move(update_fen.from_, update_fen.dest,
                                                                              pre_move_fen, player.board.grid))
            exec_player(lambda player: player.played_moves_gui.add_played_move(update_fen.from_, update_fen.dest,
                                                                               pre_move_fen, fen[update_fen.dest]))

        def process_end_game(end_game: EndGameEvent) -> None:
            exec_player(lambda player: player.end_game(end_game.result, end_game.reason))

        def process_update_captured_pieces(cap_pieces: UpdateCapturedPiecesEvent) -> None:
            exec_player(lambda player: player.captured_gui.set_captured_pieces(cap_pieces.captured_pieces))

        def process_opponent_draw_offer(draw_offer: OpponentDrawOfferEvent) -> None:
            exec_player(lambda player: player.handle_draw_offer(draw_offer.side))

        if isinstance(game_event, UpdateFenEvent):
            process_update_fen(game_event)

        elif isinstance(game_event, EndGameEvent):
            process_end_game(game_event)

        elif isinstance(game_event, InvalidMoveEvent):
            exec_player(lambda player: player.set_require_render(True))
            exec_player(lambda player: player.set_read_input(True))

        elif isinstance(game_event, UpdateCapturedPiecesEvent):
            process_update_captured_pieces(game_event)

        elif isinstance(game_event, OpponentPromotionEvent):
            exec_player(lambda player: player.set_opponent_promoting(True))

        elif isinstance(game_event, OpponentDrawOfferEvent):
            process_opponent_draw_offer(game_event)

        elif isinstance(game_event, ContinueGameEvent):
            exec_player(lambda player: player.continue_game())
            exec_player(lambda player: player.set_require_render(True))

        else:
            assert False, f" {game_event.type.name} : Command not recognised"

    @staticmethod
    def local_game_process(fen: Fen, *players: Player) -> None:
        if (game_event := LocalEvents.get().get_player_event()) is None:
            return

        Player.process_game_event(game_event, fen, *players)


def dispatch_event(connection: Optional[socket.socket], game_event: GameEvent) -> None:
    if connection is None:
        LocalEvents.get().add_match_event(game_event)
        return

    EventManager.dispatch(connection, game_event)
