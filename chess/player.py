import enum

import pygame

import chess.chess_data as CHESS
import chess.game as GAME
import utils.Forsyth_Edwards_notation as FEN
import utils.asset as ASSETS
import utils.commands as CMD
import utils.network as NET

from gui.promotion_gui import PromotionGui
from gui.captured_gui import CapturedGui



# -- Enums --
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


# -----------

class Player:
    def __init__(self,
                 side: CHESS.SIDE,
                 piece_set: ASSETS.PieceSetAssets,
                 board_asset: ASSETS.BoardAssets,
                 scale: float):
        self.side: CHESS.SIDE = side
        self.board: CHESS.Board = CHESS.get_board(board_asset.value, side, scale)
        self.pieces: dict[str, CHESS.Piece] = CHESS.get_pieces(piece_set.value, scale)
        self.turn: bool = side is CHESS.SIDE.WHITE
        self.state: STATE = STATE.PICK_PIECE
        self.is_render_required: bool = True
        self.game_over = False
        self.promotion_gui = PromotionGui(self.pieces, self.side, self.board.sprite.surface.get_rect())
        self.captured_gui = CapturedGui('', self.pieces, self.board.pos_rect,
                                        'white' if self.side is CHESS.SIDE.WHITE else 'black')
        self.prev_left_mouse_up: tuple[int, int] = 0, 0

    # -- reading playing input --
    def parse_input(
            self,
            event: pygame.event.Event,
            fen: FEN.Fen,
            network: NET.Network | None = None,
            local: bool = False) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == MOUSECLICK.LEFT.value: self.handle_mouse_down_left(network, local)
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == MOUSECLICK.LEFT.value: self.handle_left_mouse_up(network, local, fen)

    def handle_left_mouse_up(self, network: NET.Network | None, local: bool, fen: FEN.Fen) -> None:
        if self.state is not STATE.DROP_PIECE: return

        dest_board_square = CHESS.get_collided_board_square(self.board)
        from_board_square = CHESS.get_picked_up(self.board)
        from_coordinates = from_board_square.algebraic_notation.data.coordinates

        # invalid move
        target_fen = from_board_square.FEN_val
        move = CMD.get(CMD.COMMANDS.MOVE, from_coordinates, from_coordinates, self.side.name, target_fen)
        is_promotion = False

        if dest_board_square:
            is_promotion = is_pawn_promotion(from_board_square, dest_board_square, fen)
            dest_coordinates = dest_board_square.algebraic_notation.data.coordinates
            move = CMD.get(CMD.COMMANDS.MOVE, from_coordinates, dest_coordinates, self.side.name, target_fen)

        if not is_promotion:
            send_move(local, network, move)
            self.state = STATE.PICK_PIECE
            CHESS.reset_picked_up(self.board)

        else:
            self.state = STATE.PICK_PROMOTION

        self.prev_left_mouse_up = pygame.mouse.get_pos()

    def handle_mouse_down_left(self, network: NET.Network | None, local: bool) -> None:
        if self.state is STATE.DROP_PIECE: return
        if self.state is STATE.PICK_PROMOTION: self.handle_pick_promotion(local, network)
        elif self.state is STATE.PICK_PIECE:
            board_square = CHESS.get_collided_board_square(self.board)
            if not board_square: return
            if board_square.FEN_val is FEN.FenChars.BLANK_PIECE.value: return
            CHESS.set_picked_up(board_square, self.board)
            self.state = STATE.DROP_PIECE

    def handle_pick_promotion(self, local: bool, network: NET.Network | None) -> None:
        for surface, rect, val in self.promotion_gui.promotion_pieces:
            if not rect.collidepoint(pygame.mouse.get_pos()): continue
            from_board_square = CHESS.get_picked_up(self.board)
            dest_board_square = CHESS.get_collided_board_square(self.board, self.prev_left_mouse_up)
            if dest_board_square is None or from_board_square is None: continue
            from_coordinates = from_board_square.algebraic_notation.data.coordinates
            dest_coordinates = dest_board_square.algebraic_notation.data.coordinates

            move = CMD.get(CMD.COMMANDS.MOVE, from_coordinates, dest_coordinates, self.side.name, val)
            send_move(local, network, move)
            CHESS.reset_picked_up(self.board)
            self.state = STATE.PICK_PIECE
            self.is_render_required = True
    # ---------------------------

    # -- rendering players game --
    def render(self, bg_color) -> None:
        if self.is_render_required or self.state is STATE.DROP_PIECE:
            pygame.display.get_surface().fill(bg_color)
            self.render_board()
            self.render_pieces()
            self.captured_gui.render(self.side)
        if self.state is STATE.PICK_PROMOTION:
            self.promotion_gui.render()
        self.is_render_required = False

    def render_board(self) -> None:
        pygame.display.get_surface().blit(self.board.sprite.surface, self.board.pos_rect)
        if self.state is STATE.DROP_PIECE: self.show_available_moves()

    def render_pieces(self) -> None:
        grid = self.board.grid if self.side is CHESS.SIDE.WHITE else self.board.grid[::-1]
        board_offset = pygame.math.Vector2(self.board.pos_rect.topleft)
        for board_square in grid:
            if board_square.FEN_val is FEN.FenChars.BLANK_PIECE.value: continue
            if board_square.picked_up: continue
            self.render_board_square(board_square, board_offset)
        if self.state is STATE.DROP_PIECE: self.render_board_square(CHESS.get_picked_up(self.board), board_offset)

    def render_board_square(self, board_square, board_offset) -> None:
        piece_surface = self.pieces[board_square.FEN_val].sprite.surface
        pygame.display.get_surface().blit(piece_surface,
                                          CHESS.get_piece_render_pos(board_square, board_offset, piece_surface))

    def show_available_moves(self) -> None:
        if not self.turn: return
        picked = CHESS.get_picked_up(self.board)
        if self.side is CHESS.SIDE.WHITE:
            if picked.FEN_val.islower(): return
        if self.side is CHESS.SIDE.BLACK:
            if picked.FEN_val.isupper(): return
        for surface, pos in CHESS.get_available_moves_surface(picked, self.board):
            pygame.display.get_surface().blit(surface, pos)

    def update_pieces_location(self, fen: FEN.Fen) -> None:
        for index, fen_val in enumerate(fen.expanded):
            board_square = self.board.grid[index]
            board_square.FEN_val = fen_val
            update_available_moves(board_square, fen, self.side)
        self.is_render_required = True

    # ----------------------------

    # -- helpers --
    def progress_state(self) -> None:
        self.state = STATE((self.state.value + 1) % len(list(STATE)))

    def end_turn(self) -> None:
        self.turn = False
        self.game_over = True

    def update_turn(self, fen: FEN.Fen) -> None:
        if self.side is CHESS.SIDE.WHITE:
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
        opposite_side = CHESS.SIDE.WHITE if self.side is CHESS.SIDE.BLACK else CHESS.SIDE.BLACK
        return f"{opposite_side.name}s TURN"


# -------------


# -- Parsing Commands --
def parse_command(command: str, info: str, match_fen: FEN.Fen, *players: Player, local: bool = False) -> None:
    match CMD.COMMANDS(command):
        case CMD.COMMANDS.UPDATE_POS:
            if not local: match_fen.notation = info
            list(map(lambda player: player.update_pieces_location(match_fen), players))
            list(map(lambda player: player.update_turn(match_fen), players))
        case CMD.COMMANDS.END_GAME:
            list(map(lambda player: player.end_turn(), players))
        case CMD.COMMANDS.INVALID_MOVE:
            list(map(lambda player: player.set_require_render(True), players))
        case CMD.COMMANDS.UPDATE_CAP_PIECES:
            list(map(lambda player: player.captured_gui.set_captured_pieces(info), players))
        case _:
            assert False, f" {command} : Command not recognised"


def parse_command_local(match_fen: FEN.Fen, *players: Player) -> None:
    command = CMD.read_from(CMD.PLAYER)
    if command is None: return
    cmd, info = CMD.split_command_info(command.info)
    parse_command(cmd, info, match_fen, *players, local=True)


# -----------------

# --
def update_available_moves(board_square: CHESS.BoardSquare, match_fen: FEN.Fen, player_side: CHESS.SIDE) -> None:
    is_black_and_lower = player_side is CHESS.SIDE.BLACK and board_square.FEN_val.islower()
    is_white_and_upper = player_side is CHESS.SIDE.WHITE and board_square.FEN_val.isupper()
    correct_side = True if is_black_and_lower or is_white_and_upper else False
    if board_square.FEN_val == FEN.FenChars.BLANK_PIECE.value or not correct_side:
        board_square.available_moves = []
        return None
    name = CHESS.get_name_from_fen(board_square.FEN_val)
    board_square.available_moves = GAME.get_available_moves(name,
                                                            board_square.algebraic_notation.data.index,
                                                            match_fen)


def is_pawn_promotion(from_board_square: CHESS.BoardSquare, dest_board_square: CHESS.BoardSquare, fen: FEN.Fen) -> bool:
    pawn_fen = FEN.FenChars.WHITE_PAWN.value if fen.is_white_turn() else FEN.FenChars.BLACK_PAWN.value
    rank = '8' if fen.is_white_turn() else '1'
    from_index = from_board_square.algebraic_notation.data.index
    dest_index = dest_board_square.algebraic_notation.data.index
    dest_rank = dest_board_square.algebraic_notation.data.rank
    if from_board_square.FEN_val != pawn_fen: return False
    if dest_rank != rank: return False
    if dest_index not in GAME.get_available_moves('PAWN', from_index, fen): return False
    if not GAME.is_king_safe(from_board_square.algebraic_notation.data.index,
                             dest_board_square.algebraic_notation.data.index, fen): return False
    return True


def send_move(local: bool, network: NET.Network | None, move: CMD.Command) -> None:
    if local:
        CMD.send_to(CMD.MATCH, move)
    else:
        if network: network.socket.send(str.encode(move.info))
