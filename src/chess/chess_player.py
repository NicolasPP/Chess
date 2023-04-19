import datetime
import enum

import pygame

from chess.asset.asset_manager import AssetManager
from chess.board.board_tile import BoardTile
from chess.board.chess_board import Board
from chess.board.side import Side
from chess.game.game_size import GameSize
from chess.game.game_surface import GameSurface
from chess.movement.piece_movement import is_pawn_promotion
from chess.network.chess_network import ChessNetwork
from chess.network.command_manager import CommandManager, ClientCommand, ServerCommand, Command
from chess.notation.forsyth_edwards_notation import Fen, FenChars
from gui.available_moves_gui import AvailableMovesGui
from gui.board_axis_gui import BoardAxisGui
from gui.captured_gui import CapturedGui
from gui.end_game_gui import EndGameGui
from gui.promotion_gui import PromotionGui
from gui.timer_gui import TimerGui, TimerRects
from gui.verify_gui import VerifyGui
from gui.previous_move_gui import PreviousMoveGui
from config import *


class State(enum.Enum):
    PICK_PIECE = enum.auto()
    DROP_PIECE = enum.auto()
    PICKING_PROMOTION = enum.auto()
    OFFERED_DRAW = enum.auto()
    RESPOND_DRAW = enum.auto()
    DRAW_DOUBLE_CHECK = enum.auto()
    RESIGN_DOUBLE_CHECK = enum.auto()


class Player:
    def __init__(self,
                 side: Side,
                 time_left: float,
                 game_offset: pygame.rect.Rect):

        self.game_offset = game_offset
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

        self.promotion_gui: PromotionGui = PromotionGui(self.side, self.board.get_rect())
        self.captured_gui: CapturedGui = CapturedGui('', self.board.get_rect())
        self.timer_gui: TimerGui = TimerGui(time_left, self.board.get_rect())
        self.end_game_gui: EndGameGui = EndGameGui(self.board.get_rect())
        self.verify_gui: VerifyGui = VerifyGui(self.board.get_rect())
        self.axis_gui: BoardAxisGui = BoardAxisGui(self.board.get_rect(), self.side)
        self.available_moves_gui: AvailableMovesGui = AvailableMovesGui()
        self.previous_move_gui: PreviousMoveGui = PreviousMoveGui(self.board.rect)

    def parse_input(
            self,
            event: pygame.event.Event,
            fen: Fen,
            network: ChessNetwork | None = None,
            local: bool = False) -> None:
        if self.game_over: return
        if not self.read_input: return
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == MOUSECLICK_LEFT:
                self.handle_mouse_down_left(network, local)
                self.handle_end_game_mouse_down()
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == MOUSECLICK_LEFT:
                self.handle_mouse_up_left(network, local, fen)

    def handle_end_game_mouse_down(self) -> None:
        if self.state == State.RESPOND_DRAW: return
        if self.state == State.OFFERED_DRAW: return
        if self.state == State.RESIGN_DOUBLE_CHECK: return
        if self.state == State.DRAW_DOUBLE_CHECK: return
        mouse_pos = pygame.math.Vector2(pygame.mouse.get_pos()) - pygame.math.Vector2(self.game_offset.topleft)
        if self.end_game_gui.offer_draw.rect.collidepoint(mouse_pos.x, mouse_pos.y):
            self.state = State.DRAW_DOUBLE_CHECK
            self.verify_gui.set_action_label(DRAW_DOUBLE_CHECK_LABEL)
            self.end_game_gui.offer_draw.set_hover(False)
            self.end_game_gui.resign.set_hover(False)

        elif self.end_game_gui.resign.rect.collidepoint(mouse_pos.x, mouse_pos.y):
            self.state = State.RESIGN_DOUBLE_CHECK
            self.verify_gui.set_action_label(RESIGN_DOUBLE_CHECK_LABEL)
            self.end_game_gui.offer_draw.set_hover(False)
            self.end_game_gui.resign.set_hover(False)

    def handle_mouse_up_left(self, network: ChessNetwork | None, local: bool, fen: Fen) -> None:
        if self.state is not State.DROP_PIECE: return
        self.end_game_gui.offer_draw.set_hover(True)
        self.end_game_gui.resign.set_hover(True)
        dest_tile = self.board.get_collided_tile(self.game_offset)
        from_tile = self.board.get_picked_up()

        from_coordinates = from_tile.algebraic_notation.coordinates
        target_fen = from_tile.fen_val
        time_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # invalid move
        invalid_move_info: dict[str, str] = {
            CommandManager.from_coordinates: from_coordinates,
            CommandManager.dest_coordinates: from_coordinates,
            CommandManager.side: self.side.name,
            CommandManager.target_fen: target_fen,
            CommandManager.time_iso: time_iso
        }
        move = CommandManager.get(ClientCommand.MOVE, invalid_move_info)
        is_promotion = False

        if dest_tile:
            is_promotion = is_pawn_promotion(
                from_tile.algebraic_notation,
                dest_tile.algebraic_notation,
                from_tile.fen_val,
                fen
            )
            dest_coordinates = dest_tile.algebraic_notation.coordinates
            move_info: dict[str, str] = {
                CommandManager.from_coordinates: from_coordinates,
                CommandManager.dest_coordinates: dest_coordinates,
                CommandManager.side: self.side.name,
                CommandManager.target_fen: target_fen,
                CommandManager.time_iso: time_iso
            }
            move = CommandManager.get(ClientCommand.MOVE, move_info)

        if not is_promotion:
            send_command(local, network, move)
            self.set_read_input(False)
            self.state = State.PICK_PIECE
            self.board.reset_picked_up()

        else:
            self.state = State.PICKING_PROMOTION
            if not local:
                picking_promotion = CommandManager.get(ClientCommand.PICKING_PROMOTION)
                send_command(local, network, picking_promotion)

        self.prev_left_mouse_up = pygame.mouse.get_pos()
        self.prev_time_iso = time_iso

    def handle_mouse_down_left(self, network: ChessNetwork | None, local: bool) -> None:
        if self.state is State.DROP_PIECE: return
        if self.state is State.PICKING_PROMOTION:
            self.handle_pick_promotion(local, network)
        elif self.state is State.PICK_PIECE:
            tile = self.board.get_collided_tile(self.game_offset)
            if not tile: return
            if tile.fen_val == FenChars.BLANK_PIECE: return
            self.board.set_picked_up(tile)
            self.state = State.DROP_PIECE
            self.end_game_gui.offer_draw.set_hover(False)
            self.end_game_gui.resign.set_hover(False)
        elif self.state is State.RESPOND_DRAW:
            self.verify_gui.handle_response(self.game_offset)
            if self.verify_gui.result is None: return
            draw_response_info: dict[str, str] = {
                CommandManager.draw_offer_result: str(int(self.verify_gui.result))
            }
            draw_response = CommandManager.get(ClientCommand.DRAW_RESPONSE, draw_response_info)
            send_command(local, network, draw_response)
            self.verify_gui.set_result(None)
        elif self.state is State.DRAW_DOUBLE_CHECK or self.state is State.RESIGN_DOUBLE_CHECK:
            self.verify_gui.handle_response(self.game_offset)
            if self.verify_gui.result is None: return
            if not self.verify_gui.result:
                self.state = State.PICK_PIECE
                self.set_require_render(True)
                self.end_game_gui.resign.set_hover(True)
                self.end_game_gui.offer_draw.set_hover(True)
                return
            if self.state is State.DRAW_DOUBLE_CHECK:
                self.state = State.OFFERED_DRAW
                draw_info: dict[str, str] = {CommandManager.side: self.side.name}
                offer_draw = CommandManager.get(ClientCommand.OFFER_DRAW, draw_info)
                send_command(local, network, offer_draw)
            else:
                resign_info: dict[str, str] = {
                    CommandManager.side: self.side.name
                }
                resign = CommandManager.get(ClientCommand.RESIGN, resign_info)
                send_command(local, network, resign)

            self.verify_gui.set_result(None)
            self.set_require_render(True)

    def handle_pick_promotion(self, local: bool, network: ChessNetwork | None) -> None:
        for surface, rect, val in self.promotion_gui.promotion_pieces:
            mouse_pos = pygame.math.Vector2(pygame.mouse.get_pos()) - pygame.math.Vector2(self.game_offset.topleft)
            if not rect.collidepoint(mouse_pos.x, mouse_pos.y): continue
            from_tile = self.board.get_picked_up()
            dest_tile = self.board.get_collided_tile(self.game_offset, self.prev_left_mouse_up)
            if dest_tile is None or from_tile is None: continue
            from_coordinates = from_tile.algebraic_notation.coordinates
            dest_coordinates = dest_tile.algebraic_notation.coordinates

            if self.prev_time_iso is None: return
            move_info: dict[str, str] = {
                CommandManager.from_coordinates: from_coordinates,
                CommandManager.dest_coordinates: dest_coordinates,
                CommandManager.side: self.side.name,
                CommandManager.target_fen: val,
                CommandManager.time_iso: self.prev_time_iso
            }
            move = CommandManager.get(ClientCommand.MOVE, move_info)

            send_command(local, network, move)
            self.board.reset_picked_up()
            self.state = State.PICK_PIECE
            self.set_require_render(True)

    def update(self, delta_time: float, local: bool = False, network: ChessNetwork | None = None) -> None:
        if self.game_over: return
        if self.state == State.PICKING_PROMOTION: return
        if self.state == State.OFFERED_DRAW: return
        if self.state == State.RESPOND_DRAW: return
        if self.opponent_promoting: return
        if self.timed_out: return
        if self.state != State.DRAW_DOUBLE_CHECK and \
                self.state != State.RESIGN_DOUBLE_CHECK:
            self.axis_gui.update_hover_highlight(self.board.get_collided_tile(self.game_offset))
        self.timer_gui.tick(delta_time)
        if self.timer_gui.own_timer.time_left <= 0:
            time_out_info: dict[str, str] = {
                CommandManager.side: self.side.name
            }
            time_out = CommandManager.get(ClientCommand.TIME_OUT, time_out_info)
            send_command(local, network, time_out)
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
            self.end_game_gui.game_over_gui.render()
            return

        self.timer_gui.render()
        self.axis_gui.render()
        self.end_game_gui.render(pygame.math.Vector2(self.game_offset.topleft))

        if self.is_render_required or self.state is State.DROP_PIECE:
            GameSurface.get().fill(AssetManager.get_theme().dark_color)
            self.timer_gui.render()
            self.end_game_gui.render(pygame.math.Vector2(self.game_offset.topleft))
            self.captured_gui.render(self.side)
            self.board.render()
            self.axis_gui.render()
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
            self.verify_gui.render(pygame.math.Vector2(self.game_offset.topleft))

        if self.state is State.OFFERED_DRAW: pass

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
        self.render()
        self.set_turn(False)
        self.set_game_over(True)
        self.end_game_gui.game_over_gui.set_final_frame(game_result, result_type)

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
            int(Y_AXIS_WIDTH * GameSize.get_scale()),
            int(timer_rects.spacing.height + timer_rects.timer.height)
        )

    def set_read_input(self, read_input: bool) -> None:
        self.read_input = read_input

    def set_opponent_promoting(self, promoting: bool) -> None:
        self.opponent_promoting = promoting


def process_server_command(command: Command, match_fen: Fen,
                           *players: Player, local: bool = False) -> None:
    if command.name == ServerCommand.UPDATE_FEN.name:
        fen_notation: str = command.info[CommandManager.fen_notation]
        white_time: str = command.info[CommandManager.white_time_left]
        black_time: str = command.info[CommandManager.black_time_left]
        from_index: str = command.info[CommandManager.from_index]
        dest_index: str = command.info[CommandManager.dest_index]
        if not local: match_fen.notation = fen_notation
        list(map(lambda player: player.update_pieces_location(match_fen), players))
        list(map(lambda player: player.update_turn(match_fen), players))
        list(map(lambda player: player.timer_gui.update(
            player.side, match_fen.data.active_color, float(white_time), float(black_time)
        ), players))
        list(map(lambda player: player.set_read_input(True), players))
        list(map(lambda player: player.set_opponent_promoting(False), players))
        list(map(lambda player: player.previous_move_gui.set_prev_move(
            player.board.grid[int(from_index)], player.board.grid[int(dest_index)]), players))

    elif command.name == ServerCommand.END_GAME.name:
        list(map(lambda player: player.end_game(
            command.info[CommandManager.game_result], command.info[CommandManager.game_result_type]
        ), players))

    elif command.name == ServerCommand.INVALID_MOVE.name:
        list(map(lambda player: player.set_require_render(True), players))
        list(map(lambda player: player.set_read_input(True), players))

    elif command.name == ServerCommand.UPDATE_CAP_PIECES.name:
        captured_pieces: str = command.info[CommandManager.captured_pieces]
        list(map(lambda player: player.captured_gui.set_captured_pieces(captured_pieces), players))

    elif command.name == ServerCommand.CLIENT_PROMOTING.name:
        list(map(lambda player: player.set_opponent_promoting(True), players))

    elif command.name == ServerCommand.CLIENT_DRAW_OFFER.name:
        list(map(lambda player: player.handle_draw_offer(command.info[CommandManager.side]), players))

    elif command.name == ServerCommand.CONTINUE.name:
        list(map(lambda player: player.continue_game(), players))
        list(map(lambda player: player.set_require_render(True), players))

    else:
        assert False, f" {command.name} : Command not recognised"


def process_command_local(match_fen: Fen, *players: Player) -> None:
    command = CommandManager.read_from(CommandManager.PLAYER)
    if command is None: return
    process_server_command(command, match_fen, *players, local=True)


def send_command(local: bool, network: ChessNetwork | None, command: Command) -> None:
    if local:
        CommandManager.send_to(CommandManager.MATCH, command)
    else:
        if network: network.socket.send(CommandManager.serialize_command(command))
