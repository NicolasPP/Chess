import string
import typing
import pygame

from chess.notation.algebraic_notation import AlgebraicNotation
from chess.notation.forsyth_edwards_notation import FenChars
from chess.asset.asset_manager import AssetManager
from chess.piece_movement import Side
from chess.game_surface import GameSurface
from config import *


class RenderPos(typing.NamedTuple):
    x: float
    y: float


class BoardSquareIndex(typing.NamedTuple):
    row: int
    col: int
    algebraic_notation: AlgebraicNotation


class BoardSquare:

    @staticmethod
    def get_board_squares_index(side: Side) -> typing.Generator[BoardSquareIndex, None, None]:
        files = string.ascii_lowercase[:BOARD_SIZE]
        files = files[::-1] if side is Side.BLACK else files
        for rank in range(BOARD_SIZE):
            for col, file in enumerate(files):
                str_rank = str(BOARD_SIZE - rank) if side is Side.WHITE else str(rank + 1)
                yield BoardSquareIndex(rank, col, AlgebraicNotation(file, str_rank))

    def __init__(
            self,
            rect: pygame.rect.Rect,
            algebraic_notation: AlgebraicNotation,
            available_moves: list[int],
            fen_val: str = FenChars.BLANK_PIECE.value
    ):
        self.rect: pygame.rect.Rect = rect
        self.algebraic_notation: AlgebraicNotation = algebraic_notation
        self.available_moves: list[int] = available_moves
        self.fen_val: str = fen_val
        self.picked_up: bool = False

    def get_piece_render_pos(self, board_offset: pygame.math.Vector2,
                             piece_surface: pygame.surface.Surface) -> RenderPos:
        if self.picked_up: return self.get_picked_up_piece_render_pos(piece_surface, board_offset)
        return self.get_not_picked_up_piece_render_pos(board_offset, piece_surface)

    def get_not_picked_up_piece_render_pos(self, board_offset: pygame.math.Vector2,
                                           piece_surface: pygame.surface.Surface) -> RenderPos:
        piece_rect = piece_surface.get_rect(topleft=self.rect.topleft)
        piece_rect.bottom = self.rect.bottom
        pos = pygame.math.Vector2(piece_rect.x, piece_rect.y) + board_offset
        return RenderPos(pos.x, pos.y)

    def get_picked_up_piece_render_pos(self, piece_surface: pygame.surface.Surface, offset: pygame.math.Vector2)\
            -> RenderPos:
        piece_rect = piece_surface.get_rect(topleft=self.rect.topleft)
        piece_rect.midbottom = pygame.mouse.get_pos()
        result = pygame.math.Vector2(piece_rect.topleft) - offset
        return RenderPos(result.x, result.y)

    def render(self, board_pos: tuple[int, int]) -> None:
        offset = pygame.math.Vector2(board_pos)
        piece_surface = AssetManager.get_piece(self.fen_val).surface
        piece_pos: RenderPos = BoardSquare.get_piece_render_pos(self, offset, piece_surface)
        GameSurface.get().blit(piece_surface, (piece_pos.x, piece_pos.y))


class Board:

    @staticmethod
    def calculate_board_rect(scale: float) -> pygame.rect.Rect:
        return pygame.rect.Rect(
            (0, 0),
            ((SQUARE_SIZE * BOARD_SIZE * scale) + (BOARD_OUTLINE_THICKNESS * 2),
             (SQUARE_SIZE * BOARD_SIZE * scale) + (BOARD_OUTLINE_THICKNESS * 2)))

    @staticmethod
    def create_board_grid(side: Side, scale: float) -> list[BoardSquare]:
        grid = []
        size = pygame.math.Vector2(SQUARE_SIZE * scale)
        outline_thickness = pygame.math.Vector2(BOARD_OUTLINE_THICKNESS)
        for index in BoardSquare.get_board_squares_index(side):
            pos = pygame.math.Vector2(index.col * size.x, index.row * size.y)
            rect = pygame.rect.Rect(pos + outline_thickness, size)
            grid.append(BoardSquare(rect, index.algebraic_notation, []))
        if side is Side.BLACK: grid = grid[::-1]
        return grid

    @staticmethod
    def create_board_surface(board_squares: list[BoardSquare], scale: float) -> pygame.surface.Surface:
        outline_thickness = pygame.math.Vector2(BOARD_OUTLINE_THICKNESS) * 2
        size = pygame.math.Vector2(SQUARE_SIZE * scale)
        board_surface = pygame.surface.Surface((size * BOARD_SIZE) + outline_thickness)
        board_surface.fill(AssetManager.get_theme().light_color)
        counter = 0
        for board_square in board_squares:
            surface = pygame.surface.Surface(board_square.rect.size)
            if counter % 2 == 0:
                surface.fill(AssetManager.get_theme().light_color)
            else:
                surface.fill(AssetManager.get_theme().dark_color)

            if (board_square.algebraic_notation.data.index + 1) % BOARD_SIZE != 0:
                counter += 1

            board_surface.blit(surface, board_square.rect.topleft)
        return board_surface

    def __init__(self, side: Side, scale: float):
        self.grid: list[BoardSquare] = Board.create_board_grid(side, scale)
        self.surface: pygame.surface.Surface = Board.create_board_surface(self.grid, scale)
        if side is Side.BLACK:
            self.surface = pygame.transform.flip(self.surface, True, True)
        self.pos_rect: pygame.rect.Rect = self.surface.get_rect()

    def reload_theme(self, side: Side, scale: float) -> None:
        self.surface = Board.create_board_surface(self.grid, scale)
        if side is Side.BLACK:
            self.surface = pygame.transform.flip(self.surface, True, True)

    def reset_picked_up(self) -> None:
        for sqr in self.grid: sqr.picked_up = False

    def get_picked_up(self) -> BoardSquare:
        for sqr in self.grid:
            if sqr.picked_up: return sqr
        raise Exception(' no piece picked up ')

    def set_picked_up(self, board_square: BoardSquare) -> None:
        if board_square.fen_val == FenChars.BLANK_PIECE.value: return
        self.reset_picked_up()
        board_square.picked_up = True

    def get_collided_board_square(self, game_offset: pygame.rect.Rect,
                                  mouse_pos: tuple[int, int] | None = None) -> BoardSquare | None:
        if mouse_pos is None: mouse_pos = pygame.mouse.get_pos()
        board_offset = pygame.math.Vector2(self.pos_rect.topleft) + pygame.math.Vector2(game_offset.topleft)
        for board_square in self.grid:
            rect = board_square.rect.copy()
            top_left = board_offset + pygame.math.Vector2(rect.topleft)
            rect.topleft = int(top_left.x), int(top_left.y)
            if rect.collidepoint(mouse_pos):
                return board_square
        return None

    def get_available_moves_surface(self, picked: BoardSquare) -> \
            typing.Generator[tuple[pygame.surface.Surface, pygame.math.Vector2], None, None]:
        board_offset = pygame.math.Vector2(self.pos_rect.topleft)
        for index in picked.available_moves:
            board_square = self.grid[index]
            board_square_size = pygame.math.Vector2(board_square.rect.size) * AVAILABLE_MOVE_SCALE
            available_surface = pygame.surface.Surface(board_square_size)
            pos = available_surface.get_rect(center=board_square.rect.center)
            available_surface.fill(AVAILABLE_MOVE_COLOR)
            available_surface.set_alpha(AVAILABLE_ALPHA)
            yield available_surface, board_offset + pygame.math.Vector2(pos.topleft)

    def render(self) -> None:
        GameSurface.get().blit(self.surface, self.pos_rect)

    def render_pieces(self, is_white: bool) -> None:
        grid = self.grid if is_white else self.grid[::-1]
        for board_square in grid:
            if board_square.fen_val == FenChars.BLANK_PIECE.value: continue
            if board_square.picked_up: continue
            board_square.render(self.pos_rect.topleft)
