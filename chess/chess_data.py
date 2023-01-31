import dataclasses
import enum
import string
import typing

import pygame

import utils.FEN_notation as FEN
import utils.asset as ASSETS
from config import *


# -- Enums --
class PIECES(enum.Enum):
    PAWN: int = 0
    KNIGHT: int = 1
    ROOK: int = 2
    BISHOP: int = 3
    QUEEN: int = 4
    KING: int = 5

    def set_moves(self, func: typing.Callable) -> None:
        self.available_moves: typing.Callable = func

    def set_fen(self, fen_val: str) -> None:
        self.FEN_val: str = fen_val


class SIDE(enum.Enum):
    WHITE = enum.auto()
    BLACK = enum.auto()


# -----------

# -- Classes --


@dataclasses.dataclass
class BoardSquare:
    rect: pygame.rect.Rect
    AN_coordinates: str
    available_moves: list[int]
    FEN_val: str = FEN.FenChars.BLANK_PIECE.value
    picked_up: bool = False


@dataclasses.dataclass
class Board:
    sprite: ASSETS.Sprite
    pos_rect: pygame.rect.Rect
    grid: list[BoardSquare]


@dataclasses.dataclass
class Piece:
    sprite: ASSETS.Sprite
    FEN_val: str


# -------------

# -- Class Helpers --


def set_picked_up(board_square: BoardSquare, board: Board) -> None:
    if board_square.FEN_val == FEN.FenChars.BLANK_PIECE.value: return
    reset_picked_up(board)
    board_square.picked_up = True


def reset_picked_up(board: Board) -> None:
    for sqr in board.grid: sqr.picked_up = False


def is_picked_up(board: Board) -> bool:
    for sqr in board.grid:
        if sqr.picked_up: return True
    return False


def get_picked_up(board: Board) -> BoardSquare:
    for sqr in board.grid:
        if sqr.picked_up: return sqr
    raise Exception(' no piece picked up ')


def get_collided_board_square(board: Board) -> BoardSquare | None:
    board_offset = pygame.math.Vector2(board.pos_rect.topleft)
    for board_square in board.grid:
        rect = board_square.rect.copy()
        top_left = board_offset + pygame.math.Vector2(rect.topleft)
        rect.topleft = int(top_left.x), int(top_left.y)
        if rect.collidepoint(pygame.mouse.get_pos()):
            return board_square
    return None


def get_name_from_fen(fen_val: str) -> str:
    for piece in list(PIECES):
        if piece.FEN_val == fen_val.upper(): return piece.name
    raise Exception(f'FEN_val : {fen_val} not found')


def get_available_moves_surface(picked: BoardSquare, board: Board) -> \
        typing.Generator[tuple[pygame.surface.Surface, pygame.math.Vector2], None, None]:
    board_offset = pygame.math.Vector2(board.pos_rect.topleft)
    for index in picked.available_moves:
        board_square = board.grid[index]
        pos = pygame.math.Vector2(board_square.rect.topleft)
        available_surface = pygame.surface.Surface(board_square.rect.size)
        available_surface.fill(AVAILABLE_MOVE_COLOR)
        available_surface.set_alpha(AVAILABLE_ALPHA)
        yield available_surface, board_offset + pos


def get_piece_render_pos(board_square: BoardSquare, board_offset: pygame.math.Vector2,
                         piece_surface: pygame.surface.Surface) -> tuple[float, float]:
    if board_square.picked_up: return get_picked_up_piece_render_pos(board_square, piece_surface)
    return get_not_picked_up_piece_render_pos(board_square, board_offset, piece_surface)


def get_not_picked_up_piece_render_pos(board_square: BoardSquare, board_offset: pygame.math.Vector2,
                                       piece_surface: pygame.surface.Surface) -> tuple[float, float]:
    piece_rect = piece_surface.get_rect(topleft=board_square.rect.topleft)
    piece_rect.bottom = board_square.rect.bottom
    pos = pygame.math.Vector2(piece_rect.x, piece_rect.y) + board_offset
    piece_pos = pos.x, pos.y
    return piece_pos


def get_picked_up_piece_render_pos(board_square: BoardSquare, piece_surface: pygame.surface.Surface) \
        -> tuple[float, float]:
    piece_rect = piece_surface.get_rect(topleft=board_square.rect.topleft)
    piece_rect.midbottom = pygame.mouse.get_pos()
    return piece_rect.x, piece_rect.y


# -------------------

# -- getting assets --
def get_grid_surface_size(board_sprite: ASSETS.Sprite) -> pygame.math.Vector2:
    offset = pygame.math.Vector2(GRID_OFFSET) * board_sprite.factor
    board_size = pygame.math.Vector2(board_sprite.surface.get_size())
    return board_size - (offset * 2)


def board_square_info(side: SIDE) -> typing.Generator[tuple[int, int, str], None, None]:
    ranks = string.ascii_lowercase[:BOARD_SIZE]
    ranks = ranks[::-1] if side is SIDE.BLACK else ranks
    for row in range(BOARD_SIZE):
        for col, rank in zip(range(BOARD_SIZE), ranks):
            num = BOARD_SIZE - row if side is SIDE.WHITE else row + 1
            an_coordinates = str(num) + rank
            yield row, col, an_coordinates


def get_board(board_asset: ASSETS.Asset, side: SIDE, scale: float) -> Board:
    sprite = ASSETS.load_board(board_asset, scale)
    if side is SIDE.BLACK: sprite.surface = pygame.transform.flip(sprite.surface, True, True)

    pos_rect = sprite.surface.get_rect()
    grid = create_grid(sprite, pos_rect, side)
    return Board(sprite, pos_rect, grid)


def get_pieces(piece_set: ASSETS.PieceSet, scale: float) -> dict[str, Piece]:
    white_sprites, black_sprites = ASSETS.load_piece_set(piece_set, scale)
    assert len(white_sprites) == len(black_sprites)
    pieces = {}
    ''' get fen value from name of PIECES(Enum) '''

    for i in range(len(white_sprites)):
        white_fen: str = PIECES(i).FEN_val
        black_fen: str = PIECES(i).FEN_val.lower()
        pieces[white_fen] = Piece(white_sprites[i], white_fen)
        pieces[black_fen] = Piece(black_sprites[i], black_fen)

    return pieces


def create_grid(board_sprite: ASSETS.Sprite, pos_rect: pygame.rect.Rect, side: SIDE) -> list[BoardSquare]:
    grid = []
    size = get_grid_surface_size(board_sprite) / BOARD_SIZE
    board_offset = pygame.math.Vector2(pos_rect.topleft)
    grid_offset = pygame.math.Vector2(GRID_OFFSET) * board_sprite.factor
    for row, col, an_coordinates in board_square_info(side):
        pos = pygame.math.Vector2(col * size.x, row * size.y)
        rect = pygame.rect.Rect(pos + board_offset + grid_offset, size)
        grid.append(BoardSquare(rect, an_coordinates, []))
    if side is SIDE.BLACK: grid = grid[::-1]
    return grid

# --------------------------
