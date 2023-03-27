import enum
import datetime

import pygame

import chess.board as chess_board
import chess.piece as chess_piece
from utils.forsyth_edwards_notation import Fen, FenChars
from utils.asset import PieceSetAssets, BoardAssets
from gui.timer_gui import TimerGui
import utils.commands as command_manager
import utils.network as network_manager

from gui.promotion_gui import PromotionGui
from gui.captured_gui import CapturedGui

from config import I_SPLIT


class MOUSECLICK(enum.Enum):
    LEFT: int = 1
    MIDDLE: int = 2
    RIGHT: int = 3
    SCROLL_UP: int = 4
    SCROLL_DOWN: int = 5


class STATE(enum.Enum):
    PICK_PIECE: int = 0
    DROP_PIECE: int = 1
    PICK_PROMOTION: int = 2


class Player:
    def __init__(self,
                 side: chess_board.SIDE,
                 piece_set: PieceSetAssets,
                 board_asset: BoardAssets,
                 scale: float,
                 time_left: float):
        chess_piece.Pieces.load(piece_set.value, scale)
        self.side: chess_board.SIDE = side
        self.board: chess_board.Board = chess_board.Board(board_asset.value, side, scale)
        self.turn: bool = side is chess_board.SIDE.WHITE
        self.state: STATE = STATE.PICK_PIECE
        self.is_render_required: bool = True
        self.game_over = False
        self.promotion_gui = PromotionGui(self.side, self.board.sprite.surface.get_rect())
        self.captured_gui = CapturedGui('', self.board.pos_rect,
                                        'white' if self.side is chess_board.SIDE.WHITE else 'black', scale)
        self.timer_gui = TimerGui(time_left, self.board.pos_rect)
        self.prev_left_mouse_up: tuple[int, int] = 0, 0
        self.prev_time_iso: datetime.datetime | None = None
        self.read_input: bool = True
        self.opponent_promoting: bool = False

    def parse_input(
            self,
            event: pygame.event.Event,
            fen: Fen,
            network: network_manager.ChessNetwork | None = None,
            local: bool = False) -> None:
        if not self.read_input: return
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == MOUSECLICK.LEFT.value: self.handle_mouse_down_left(network, local)
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == MOUSECLICK.LEFT.value: self.handle_left_mouse_up(network, local, fen)

    def handle_left_mouse_up(self, network: network_manager.ChessNetwork | None, local: bool, fen: Fen) -> None:
        if self.state is not STATE.DROP_PIECE: return

        dest_board_square = self.board.get_collided_board_square()
        from_board_square = self.board.get_picked_up()
        from_coordinates = from_board_square.algebraic_notation.data.coordinates

        # invalid move
        time_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        target_fen = from_board_square.fen_val
        move = command_manager.get(
            command_manager.COMMANDS.MOVE,
            from_coordinates,
            from_coordinates,
            self.side.name,
            target_fen,
            time_iso
        )
        is_promotion = False

        if dest_board_square:
            is_promotion = is_pawn_promotion(from_board_square, dest_board_square, fen)
            dest_coordinates = dest_board_square.algebraic_notation.data.coordinates
            move = command_manager.get(
                command_manager.COMMANDS.MOVE,
                from_coordinates,
                dest_coordinates,
                self.side.name,
                target_fen,
                time_iso
            )

        if not is_promotion:
            send_move(local, network, move)
            self.set_read_input(False)
            self.state = STATE.PICK_PIECE
            self.board.reset_picked_up()

        else:
            self.state = STATE.PICK_PROMOTION
            network.socket.send(str.encode(command_manager.COMMANDS.PICKING_PROMOTION.value))

        self.prev_left_mouse_up = pygame.mouse.get_pos()
        self.prev_time_iso = time_iso

    def handle_mouse_down_left(self, network: network_manager.ChessNetwork | None, local: bool) -> None:
        if self.state is STATE.DROP_PIECE: return
        if self.state is STATE.PICK_PROMOTION:
            self.handle_pick_promotion(local, network)
        elif self.state is STATE.PICK_PIECE:
            board_square = self.board.get_collided_board_square()
            if not board_square: return
            if board_square.fen_val == FenChars.BLANK_PIECE.value: return
            self.board.set_picked_up(board_square)
            self.state = STATE.DROP_PIECE

    def handle_pick_promotion(self, local: bool, network: network_manager.ChessNetwork | None) -> None:
        for surface, rect, val in self.promotion_gui.promotion_pieces:
            if not rect.collidepoint(pygame.mouse.get_pos()): continue
            from_board_square = self.board.get_picked_up()
            dest_board_square = self.board.get_collided_board_square(self.prev_left_mouse_up)
            if dest_board_square is None or from_board_square is None: continue
            from_coordinates = from_board_square.algebraic_notation.data.coordinates
            dest_coordinates = dest_board_square.algebraic_notation.data.coordinates

            if self.prev_time_iso is None: return

            move = command_manager.get(
                command_manager.COMMANDS.MOVE,
                from_coordinates,
                dest_coordinates,
                self.side.name,
                val,
                self.prev_time_iso
            )

            send_move(local, network, move)
            self.board.reset_picked_up()
            self.state = STATE.PICK_PIECE
            self.is_render_required = True

    def update(self, delta_time: float) -> None:
        if self.state == STATE.PICK_PROMOTION: return
        if self.opponent_promoting: return
        self.timer_gui.tick(delta_time)

    def render(self, fg_color: str, bg_color: str) -> None:
        if self.is_render_required or self.state is STATE.DROP_PIECE:
            pygame.display.get_surface().fill(bg_color)
            self.captured_gui.render(self.side)
            self.render_board()
        if self.state is STATE.PICK_PROMOTION:
            self.promotion_gui.render()
        self.is_render_required = False
        self.timer_gui.render(fg_color, bg_color)

    def render_board(self) -> None:
        pygame.display.get_surface().blit(self.board.sprite.surface, self.board.pos_rect)
        if self.state is STATE.DROP_PIECE: self.show_available_moves()
        self.render_pieces()

    def render_pieces(self) -> None:
        def render_board_square(bs: chess_board.BoardSquare,
                                offset: pygame.math.Vector2) -> None:
            piece_surface = chess_piece.Pieces.sprites[bs.fen_val].surface
            piece_pos: chess_board.RenderPos = chess_board.BoardSquare.get_piece_render_pos(bs, offset, piece_surface)
            pygame.display.get_surface().blit(piece_surface, (piece_pos.x, piece_pos.y))

        grid = self.board.grid if self.side is chess_board.SIDE.WHITE else self.board.grid[::-1]
        board_offset = pygame.math.Vector2(self.board.pos_rect.topleft)
        for board_square in grid:
            if board_square.fen_val == FenChars.BLANK_PIECE.value: continue
            if board_square.picked_up: continue
            render_board_square(board_square, board_offset)
        if self.state is STATE.DROP_PIECE: render_board_square(self.board.get_picked_up(), board_offset)

    def show_available_moves(self) -> None:
        if not self.turn: return
        picked = self.board.get_picked_up()
        if self.side is chess_board.SIDE.WHITE:
            if picked.fen_val.islower(): return
        if self.side is chess_board.SIDE.BLACK:
            if picked.fen_val.isupper(): return
        for surface, pos in self.board.get_available_moves_surface(picked):
            pygame.display.get_surface().blit(surface, pos)

    def update_pieces_location(self, fen: Fen) -> None:
        for index, fen_val in enumerate(fen.expanded):
            board_square = self.board.grid[index]
            board_square.fen_val = fen_val
            update_available_moves(board_square, fen, self.side)
        self.is_render_required = True

    def progress_state(self) -> None:
        self.state = STATE((self.state.value + 1) % len(list(STATE)))

    def end_game(self) -> None:
        self.turn = False
        self.game_over = True

    def update_turn(self, fen: Fen) -> None:
        if self.side is chess_board.SIDE.WHITE:
            if fen.is_white_turn():
                self.turn = True
            else:
                self.turn = False
        else:
            if not fen.is_white_turn():
                self.turn = True
            else:
                self.turn = False

    def set_require_render(self, is_render_required: bool) -> None:
        self.is_render_required = is_render_required

    def get_window_title(self):
        if self.turn: return f"{self.side.name}s TURN"
        opposite_side = chess_board.SIDE.WHITE if self.side is chess_board.SIDE.BLACK else chess_board.SIDE.BLACK
        return f"{opposite_side.name}s TURN"

    def center_board(self, window_size: pygame.math.Vector2) -> None:
        screen_center = window_size / 2
        self.board.pos_rect.center = round(screen_center.x), round(screen_center.y)
        self.timer_gui.recalculate_pos()

    def set_read_input(self, read_input: bool) -> None:
        self.read_input = read_input

    def set_opponent_promoting(self, promoting: bool) -> None:
        self.opponent_promoting = promoting


def parse_command(command: str, info: str, match_fen: Fen,
                  *players: Player, local: bool = False) -> None:
    match command_manager.COMMANDS(command):
        case command_manager.COMMANDS.UPDATE_FEN:
            match_info, white_time, black_time = info.split(I_SPLIT)
            if not local: match_fen.notation = match_info
            list(map(lambda player: player.update_pieces_location(match_fen), players))
            list(map(lambda player: player.update_turn(match_fen), players))
            list(map(lambda player: player.timer_gui.update(
                player.side, match_fen.data.active_color, float(white_time), float(black_time)
            ), players))
            list(map(lambda player: player.set_read_input(True), players))
            list(map(lambda player: player.set_opponent_promoting(False), players))
        case command_manager.COMMANDS.END_GAME:
            list(map(lambda player: player.end_game(), players))
        case command_manager.COMMANDS.INVALID_MOVE:
            list(map(lambda player: player.set_require_render(True), players))
            list(map(lambda player: player.set_read_input(True), players))
        case command_manager.COMMANDS.UPDATE_CAP_PIECES:
            list(map(lambda player: player.captured_gui.set_captured_pieces(info), players))
        case command_manager.COMMANDS.PICKING_PROMOTION:
            list(map(lambda player: player.set_opponent_promoting(True), players))
        case _:
            assert False, f" {command} : Command not recognised"


def parse_command_local(match_fen: Fen, *players: Player) -> None:
    command = command_manager.read_from(command_manager.PLAYER)
    if command is None: return
    cmd, info = command_manager.split_command_info(command.info)
    parse_command(cmd, info, match_fen, *players, local=True)


def update_available_moves(board_square: chess_board.BoardSquare, match_fen: Fen,
                           player_side: chess_board.SIDE) -> None:
    is_black_and_lower = player_side is chess_board.SIDE.BLACK and board_square.fen_val.islower()
    is_white_and_upper = player_side is chess_board.SIDE.WHITE and board_square.fen_val.isupper()
    correct_side = True if is_black_and_lower or is_white_and_upper else False
    if board_square.fen_val == FenChars.BLANK_PIECE.value or not correct_side:
        board_square.available_moves = []
        return None
    board_square.available_moves = chess_piece.get_available_moves(
        board_square.fen_val,
        board_square.algebraic_notation.data.index,
        match_fen
    )


def is_pawn_promotion(from_board_square: chess_board.BoardSquare,
                      dest_board_square: chess_board.BoardSquare, fen: Fen) -> bool:
    pawn_fen = FenChars.DEFAULT_PAWN.get_piece_fen(fen.is_white_turn())
    rank = '8' if fen.is_white_turn() else '1'
    from_index = from_board_square.algebraic_notation.data.index
    dest_index = dest_board_square.algebraic_notation.data.index
    dest_rank = dest_board_square.algebraic_notation.data.rank
    if from_board_square.fen_val != pawn_fen: return False
    if dest_rank != rank: return False
    if dest_index not in chess_piece.get_available_moves(FenChars.DEFAULT_PAWN.value, from_index, fen): return False
    if not chess_piece.is_king_safe(from_board_square.algebraic_notation.data.index,
                                    dest_board_square.algebraic_notation.data.index, fen): return False
    return True


def send_move(local: bool, network: network_manager.ChessNetwork | None, move: command_manager.Command) -> None:
    if local:
        command_manager.send_to(command_manager.MATCH, move)
    else:
        if network: network.socket.send(str.encode(move.info))
