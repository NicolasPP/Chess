import enum
import typing

import pygame

import chess.chess_data as CHESS
import chess.game as GAME
import utils.FEN_notation as FEN
import utils.asset as ASSETS
import utils.commands as CMD
import utils.network as NET


# -- Enums --
class MOUSECLICK(enum.Enum):
    LEFT: int = 1
    MIDDLE: int = 2
    RIGHT: int = 3
    SCROLL_UP: int = 4
    SCROLL_DOWN: int = 5


class STATE(enum.Enum):
    PICK_PIECE: int = 0  # picking a piece
    DROP_PIECE: int = 1  # dropping the piece


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

    # -- reading playing input --
    def parse_input(
            self,
            event: pygame.event.Event,
            network: NET.Network | None = None,
            local: bool = False) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == MOUSECLICK.LEFT.value: self.handle_mouse_down_left()
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == MOUSECLICK.LEFT.value: self.handle_left_mouse_up(network, local)

    def handle_left_mouse_up(self, network: NET.Network | None, local: bool) -> None:
        if self.state is not STATE.DROP_PIECE: return

        board_square = CHESS.get_collided_board_square(self.board)
        from_coordinates = CHESS.get_picked_up(self.board).AN_coordinates

        move = CMD.get(CMD.COMMANDS.MOVE, from_coordinates, from_coordinates, self.side.name)
        if board_square:
            dest_coordinates = board_square.AN_coordinates
            move = CMD.get(CMD.COMMANDS.MOVE, from_coordinates, dest_coordinates, self.side.name)

        if local:
            CMD.send_to(CMD.MATCH, move)
        else:
            if network: network.socket.send(str.encode(move.info))

        self.progress_state()
        CHESS.reset_picked_up(self.board)

    def handle_mouse_down_left(self) -> None:

        board_square = CHESS.get_collided_board_square(self.board)
        if not board_square: return None
        if self.state is not STATE.PICK_PIECE: return
        if board_square.FEN_val is FEN.FenChars.BLANK_PIECE.value: return

        CHESS.set_picked_up(board_square, self.board)
        self.progress_state()

    # ---------------------------

    # -- rendering players game --
    def render(self, bg_color):
        if self.is_render_required or self.state is STATE.DROP_PIECE:
            pygame.display.get_surface().fill(bg_color)
            self.render_board()
            self.render_pieces()
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
        for piece_fen, board_square in self.fen_to_piece_board_square(fen):
            board_square.FEN_val = piece_fen
            update_available_moves(board_square, fen, self.side)
        self.is_render_required = True

    def fen_to_piece_board_square(self, fen: FEN.Fen) \
            -> typing.Generator[tuple[str, CHESS.BoardSquare], None, None]:
        count = 0
        print(fen.notation)
        for piece_fen in FEN.iterate(fen.notation):
            if piece_fen.isnumeric():
                count += int(piece_fen) - 1
                yield FEN.FenChars.BLANK_PIECE.value, self.board.grid[count]
            else:
                yield piece_fen, self.board.grid[count]
            count += 1

    # ----------------------------

    # -- helpers --
    def progress_state(self) -> None:
        self.state = STATE((self.state.value + 1) % len(list(STATE)))

    def swap_turn(self) -> None:
        self.turn = not self.turn

    def set_require_render(self, is_render_required: bool) -> None:
        self.is_render_required = is_render_required


# -------------


# -- Parsing Commands --
def parse_command(command: str, info: str, match_fen: FEN.Fen, *players: Player, local: bool = False) -> None:
    match CMD.COMMANDS(command):
        case CMD.COMMANDS.UPDATE_POS:
            if not local: match_fen = FEN.Fen(fen_notation=info)
            list(map(lambda player: player.update_pieces_location(match_fen), players))
        case CMD.COMMANDS.NEXT_TURN:
            list(map(lambda player: player.swap_turn(), players))
        case CMD.COMMANDS.INVALID_MOVE:
            list(map(lambda player: player.set_require_render(True), players))
        case _:
            assert False, f" {command} : Command not recognised"


def parse_command_local(match_fen: FEN.Fen, *players: Player) -> None:
    command = CMD.read_from(CMD.PLAYER)
    if command is None: return
    parse_command(command.info, ' ', match_fen, *players, local=True)


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
                                                            FEN.get_index_from_anc(board_square.AN_coordinates),
                                                            match_fen,
                                                            player_side is CHESS.SIDE.WHITE)
