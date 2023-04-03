import enum
import datetime

import pygame

from chess.asset.asset_manager import AssetManager
from chess.piece_movement import Side, PieceMovement, get_available_moves, is_king_safe
from chess.board import Board, BoardSquare
from chess.notation.forsyth_edwards_notation import Fen, FenChars
from chess.asset.chess_assets import PieceSetAsset, BoardAsset
from chess.network.command_manager import CommandManager, ClientCommand, ServerCommand, Command
from chess.network.chess_network import ChessNetwork
from gui.timer_gui import TimerGui
from gui.end_game_gui import EndGameGui
from gui.promotion_gui import PromotionGui
from gui.captured_gui import CapturedGui
from gui.yes_or_gui import YesOrNoGui

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
                 piece_set: PieceSetAsset,
                 board_asset: BoardAsset,
                 scale: float,
                 time_left: float):
        AssetManager.load_pieces(piece_set, scale)
        AssetManager.load_board(board_asset, scale)
        PieceMovement.load()

        self.board: Board = Board(side, scale)
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

        self.promotion_gui: PromotionGui = PromotionGui(self.side, self.board.board_sprite.sprite.surface.get_rect())
        self.captured_gui: CapturedGui = CapturedGui('', self.board.pos_rect, self.board.board_sprite.background, scale)
        self.timer_gui: TimerGui = TimerGui(time_left, self.board.pos_rect,
                                            self.board.board_sprite.background, self.board.board_sprite.foreground)
        self.end_game_gui: EndGameGui = EndGameGui(self.board.pos_rect,
                                                   self.board.board_sprite.background,
                                                   self.board.board_sprite.foreground)
        self.yes_or_no_gui: YesOrNoGui = YesOrNoGui(self.board.pos_rect)

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
                self.handle_left_mouse_up(network, local, fen)

    def handle_end_game_mouse_down(self) -> None:
        if self.state == State.RESPOND_DRAW: return
        if self.state == State.OFFERED_DRAW: return
        if self.state == State.RESIGN_DOUBLE_CHECK: return
        if self.state == State.DRAW_DOUBLE_CHECK: return
        mouse_pos: tuple[int, int] = pygame.mouse.get_pos()
        if self.end_game_gui.offer_draw.rect.collidepoint(mouse_pos):
            self.state = State.DRAW_DOUBLE_CHECK
            self.yes_or_no_gui.set_action_label(DRAW_DOUBLE_CHECK_LABEL)
            self.end_game_gui.offer_draw.set_hover(False)
            self.end_game_gui.resign.set_hover(False)

        elif self.end_game_gui.resign.rect.collidepoint(mouse_pos):
            self.state = State.RESIGN_DOUBLE_CHECK
            self.yes_or_no_gui.set_action_label(RESIGN_DOUBLE_CHECK_LABEL)
            self.end_game_gui.offer_draw.set_hover(False)
            self.end_game_gui.resign.set_hover(False)

    def handle_left_mouse_up(self, network: ChessNetwork | None, local: bool, fen: Fen) -> None:
        if self.state is not State.DROP_PIECE: return

        dest_board_square = self.board.get_collided_board_square()
        from_board_square = self.board.get_picked_up()

        from_coordinates = from_board_square.algebraic_notation.data.coordinates
        target_fen = from_board_square.fen_val
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

        if dest_board_square:
            is_promotion = is_pawn_promotion(from_board_square, dest_board_square, fen)
            dest_coordinates = dest_board_square.algebraic_notation.data.coordinates
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
            board_square = self.board.get_collided_board_square()
            if not board_square: return
            if board_square.fen_val == FenChars.BLANK_PIECE.value: return
            self.board.set_picked_up(board_square)
            self.state = State.DROP_PIECE
        elif self.state is State.RESPOND_DRAW:
            self.handle_yes_or_no_response()
            if self.yes_or_no_gui.result is None: return
            draw_response_info: dict[str, str] = {
                CommandManager.draw_offer_result: str(int(self.yes_or_no_gui.result))
            }
            draw_response = CommandManager.get(ClientCommand.DRAW_RESPONSE, draw_response_info)
            send_command(local, network, draw_response)
            self.yes_or_no_gui.set_result(None)
        elif self.state is State.DRAW_DOUBLE_CHECK or self.state is State.RESIGN_DOUBLE_CHECK:
            self.handle_yes_or_no_response()
            if self.yes_or_no_gui.result is None: return
            if not self.yes_or_no_gui.result:
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

            self.yes_or_no_gui.set_result(None)
            self.set_require_render(True)

    def handle_pick_promotion(self, local: bool, network: ChessNetwork | None) -> None:
        for surface, rect, val in self.promotion_gui.promotion_pieces:
            if not rect.collidepoint(pygame.mouse.get_pos()): continue
            from_board_square = self.board.get_picked_up()
            dest_board_square = self.board.get_collided_board_square(self.prev_left_mouse_up)
            if dest_board_square is None or from_board_square is None: continue
            from_coordinates = from_board_square.algebraic_notation.data.coordinates
            dest_coordinates = dest_board_square.algebraic_notation.data.coordinates

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
            self.yes_or_no_gui.set_action_label('')
            self.yes_or_no_gui.set_description_label(RESPOND_DRAW_LABEL)

    def handle_yes_or_no_response(self) -> None:
        mouse_pos: tuple[int, int] = pygame.mouse.get_pos()
        if self.yes_or_no_gui.yes.rect.collidepoint(mouse_pos):
            self.yes_or_no_gui.set_result(True)

        elif self.yes_or_no_gui.no.rect.collidepoint(mouse_pos):
            self.yes_or_no_gui.set_result(False)

    def continue_game(self) -> None:
        self.end_game_gui.offer_draw.set_hover(True)
        self.end_game_gui.resign.set_hover(True)
        self.state = State.PICK_PIECE

    def render(self) -> None:
        if self.game_over:
            self.end_game_gui.game_over_gui.render()
            return

        if self.is_render_required or self.state is State.DROP_PIECE:
            pygame.display.get_surface().fill(self.board.board_sprite.background)
            self.captured_gui.render(self.side)
            self.board.render()
            self.board.render_pieces(self.side is Side.WHITE)
            if self.state is State.DROP_PIECE:
                self.show_available_moves()
                self.board.get_picked_up().render(self.board.pos_rect.topleft)

        if self.state is State.PICKING_PROMOTION:
            self.promotion_gui.render()

        if self.state is State.RESPOND_DRAW or \
                self.state is State.DRAW_DOUBLE_CHECK or \
                self.state is State.RESIGN_DOUBLE_CHECK:
            self.yes_or_no_gui.render()

        if self.state is State.OFFERED_DRAW: pass

        self.set_require_render(False)
        self.timer_gui.render()
        self.end_game_gui.render()

    def show_available_moves(self) -> None:
        if not self.turn: return
        picked = self.board.get_picked_up()
        if self.side is Side.WHITE:
            if picked.fen_val.islower(): return
        if self.side is Side.BLACK:
            if picked.fen_val.isupper(): return
        for surface, pos in self.board.get_available_moves_surface(picked):
            pygame.display.get_surface().blit(surface, pos)

    def update_pieces_location(self, fen: Fen) -> None:
        for index, fen_val in enumerate(fen.expanded):
            board_square = self.board.grid[index]
            board_square.fen_val = fen_val
            update_available_moves(board_square, fen, self.side)
        self.set_require_render(True)

    def end_game(self) -> None:
        self.state = State.PICK_PIECE
        self.set_require_render(True)
        self.render()
        self.set_turn(False)
        self.set_game_over(True)
        self.end_game_gui.game_over_gui.set_final_frame()

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

    def get_window_title(self):
        if self.turn: return f"{self.side.name}s TURN"
        opposite_side = Side.WHITE if self.side is Side.BLACK else Side.BLACK
        return f"{opposite_side.name}s TURN"

    def set_to_default_pos(self, window_size: pygame.math.Vector2) -> None:
        screen_center = window_size / 2
        self.board.pos_rect.center = round(screen_center.x), round(screen_center.y)
        self.board.pos_rect.x = 0
        self.timer_gui.recalculate_pos()
        self.end_game_gui.recalculate_pos()
        self.yes_or_no_gui.recalculate_pos()

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
        if not local: match_fen.notation = fen_notation
        list(map(lambda player: player.update_pieces_location(match_fen), players))
        list(map(lambda player: player.update_turn(match_fen), players))
        list(map(lambda player: player.timer_gui.update(
            player.side, match_fen.data.active_color, float(white_time), float(black_time)
        ), players))
        list(map(lambda player: player.set_read_input(True), players))
        list(map(lambda player: player.set_opponent_promoting(False), players))

    elif command.name == ServerCommand.END_GAME.name:
        print(command.info[CommandManager.game_result_type])
        print(command.info[CommandManager.game_result])
        list(map(lambda player: player.end_game(), players))

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


def update_available_moves(board_square: BoardSquare, match_fen: Fen,
                           player_side: Side) -> None:
    is_black_and_lower = player_side is Side.BLACK and board_square.fen_val.islower()
    is_white_and_upper = player_side is Side.WHITE and board_square.fen_val.isupper()
    correct_side = True if is_black_and_lower or is_white_and_upper else False
    if board_square.fen_val == FenChars.BLANK_PIECE.value or not correct_side:
        board_square.available_moves = []
        return None
    board_square.available_moves = get_available_moves(
        board_square.fen_val,
        board_square.algebraic_notation.data.index,
        match_fen
    )


def is_pawn_promotion(from_board_square: BoardSquare,
                      dest_board_square: BoardSquare, fen: Fen) -> bool:
    pawn_fen = FenChars.DEFAULT_PAWN.get_piece_fen(fen.is_white_turn())
    rank = '8' if fen.is_white_turn() else '1'
    from_index = from_board_square.algebraic_notation.data.index
    dest_index = dest_board_square.algebraic_notation.data.index
    dest_rank = dest_board_square.algebraic_notation.data.rank
    if from_board_square.fen_val != pawn_fen: return False
    if dest_rank != rank: return False
    if dest_index not in get_available_moves(FenChars.DEFAULT_PAWN.value, from_index, fen): return False
    if not is_king_safe(from_board_square.algebraic_notation.data.index,
                        dest_board_square.algebraic_notation.data.index, fen): return False
    return True


def send_command(local: bool, network: ChessNetwork | None, command: Command) -> None:
    if local:
        CommandManager.send_to(CommandManager.MATCH, command)
    else:
        if network: network.socket.send(CommandManager.serialize_command(command))
