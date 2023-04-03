from __future__ import annotations

import string
import typing
import pygame


from chess.notation.algebraic_notation import AlgebraicNotation
from chess.notation.forsyth_edwards_notation import FenChars
from chess.asset.asset_manager import AssetManager
from chess.piece_movement import Side
from chess.asset.chess_assets import Sprite, BoardSprite
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
    def create_board_grid(board_sprite: Sprite, pos_rect: pygame.rect.Rect, side: Side) -> \
            list[BoardSquare]:
        grid = []
        size = Board.get_grid_surface_size(board_sprite) / BOARD_SIZE
        board_offset = pygame.math.Vector2(pos_rect.topleft)
        grid_offset = pygame.math.Vector2(GRID_OFFSET) * board_sprite.scale

        # don't really know why the white perspective is offset by a pixel on each axis
        # but it is so here we are
        white_offset = pygame.math.Vector2(1)

        for index in BoardSquare.get_board_squares_index(side):
            pos = pygame.math.Vector2(index.col * size.x, index.row * size.y)
            if side is Side.WHITE: pos += white_offset
            rect = pygame.rect.Rect(pos + board_offset + grid_offset, size)
            grid.append(BoardSquare(rect, index.algebraic_notation, []))
        if side is Side.BLACK: grid = grid[::-1]
        return grid

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
        if self.picked_up: return self.get_picked_up_piece_render_pos(piece_surface)
        return self.get_not_picked_up_piece_render_pos(board_offset, piece_surface)

    def get_not_picked_up_piece_render_pos(self, board_offset: pygame.math.Vector2,
                                           piece_surface: pygame.surface.Surface) -> RenderPos:
        piece_rect = piece_surface.get_rect(topleft=self.rect.topleft)
        piece_rect.bottom = self.rect.bottom
        pos = pygame.math.Vector2(piece_rect.x, piece_rect.y) + board_offset
        return RenderPos(pos.x, pos.y)

    def get_picked_up_piece_render_pos(self, piece_surface: pygame.surface.Surface) \
            -> RenderPos:
        piece_rect = piece_surface.get_rect(topleft=self.rect.topleft)
        piece_rect.midbottom = pygame.mouse.get_pos()
        return RenderPos(piece_rect.x, piece_rect.y)

    def render(self, board_pos: tuple[int, int]) -> None:
        offset = pygame.math.Vector2(board_pos)
        piece_surface = AssetManager.get_piece(self.fen_val).surface
        piece_pos: RenderPos = BoardSquare.get_piece_render_pos(self, offset, piece_surface)
        pygame.display.get_surface().blit(piece_surface, (piece_pos.x, piece_pos.y))


class Board:

    @staticmethod
    def get_grid_surface_size(board_sprite: Sprite) -> pygame.math.Vector2:
        offset = pygame.math.Vector2(GRID_OFFSET * board_sprite.scale)
        board_size = pygame.math.Vector2(board_sprite.surface.get_size())
        return board_size - (offset * 2)

    def __init__(self, side: Side, scale: float):
        self.board_sprite: BoardSprite = AssetManager.get_board()
        replace_board_axis_vals(self.board_sprite.sprite, scale, side)
        if side is Side.BLACK:
            self.board_sprite.sprite.surface = pygame.transform.flip(self.board_sprite.sprite.surface, True, True)
        self.pos_rect: pygame.rect.Rect = self.board_sprite.sprite.surface.get_rect()
        self.grid: list[BoardSquare] = BoardSquare.create_board_grid(self.board_sprite.sprite, self.pos_rect, side)

    def init_board_asset(self, side: Side, scale: float) -> None:
        self.board_sprite: BoardSprite = AssetManager.get_board()
        replace_board_axis_vals(self.board_sprite.sprite, scale, side)
        if side is Side.BLACK:
            self.board_sprite.sprite.surface = pygame.transform.flip(self.board_sprite.sprite.surface, True, True)

    def reset_picked_up(self) -> None:
        for sqr in self.grid: sqr.picked_up = False

    def is_picked_up(self) -> bool:
        for sqr in self.grid:
            if sqr.picked_up: return True
        return False

    def get_picked_up(self) -> BoardSquare:
        for sqr in self.grid:
            if sqr.picked_up: return sqr
        raise Exception(' no piece picked up ')

    def set_picked_up(self, board_square: BoardSquare) -> None:
        if board_square.fen_val == FenChars.BLANK_PIECE.value: return
        self.reset_picked_up()
        board_square.picked_up = True

    def get_collided_board_square(self, mouse_pos: tuple[int, int] | None = None) -> BoardSquare | None:
        if mouse_pos is None: mouse_pos = pygame.mouse.get_pos()
        board_offset = pygame.math.Vector2(self.pos_rect.topleft)
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
        pygame.display.get_surface().blit(self.board_sprite.sprite.surface, self.pos_rect)

    def render_pieces(self, is_white: bool) -> None:
        grid = self.grid if is_white else self.grid[::-1]
        for board_square in grid:
            if board_square.fen_val == FenChars.BLANK_PIECE.value: continue
            if board_square.picked_up: continue
            board_square.render(self.pos_rect.topleft)


def replace_board_axis_info(board_sprite: Sprite) -> \
        typing.Generator[tuple[int, pygame.rect.Rect], None, None]:
    size = Board.get_grid_surface_size(board_sprite) / BOARD_SIZE
    board_offset = pygame.math.Vector2(board_sprite.surface.get_rect().topleft)
    grid_offset = pygame.math.Vector2(GRID_OFFSET) * board_sprite.scale

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            index = (row * BOARD_SIZE) + col
            pos = pygame.math.Vector2(col * size.x, row * size.y)
            rect = pygame.rect.Rect(pos + board_offset + grid_offset, size)
            yield index, rect


def replace_board_axis_vals(board_sprite: Sprite, scale: float, side: Side) -> None:
    nums = list(range(8, 0, -1))
    nums_index = 0
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    letters_index = 0
    color = board_sprite.surface.get_at((0, 0))
    font = pygame.font.Font(FONT_FILE, 25)
    is_black_turn = True if side is Side.BLACK else False
    anti_alias: bool = False
    font_color: tuple[int, int, int] = 255, 255, 255
    for index, rect in replace_board_axis_info(board_sprite):
        if index % 8 == 0:
            val = font.render(str(nums[nums_index]), anti_alias, font_color)

            size: tuple[float, float] = 6 * scale, rect.height
            surface = pygame.surface.Surface(size)

            pos_rect = surface.get_rect()
            pos_rect.topright = rect.topleft
            pos_rect.x -= 4

            val_pos = val.get_rect()
            val_pos.center = surface.get_rect().center

            surface.fill(color)

            if is_black_turn:
                val = pygame.transform.flip(val, True, True)

            surface.blit(val, val_pos)
            board_sprite.surface.blit(surface, pos_rect)

            nums_index += 1
        if index >= 56:
            val = font.render(letters[letters_index], anti_alias, font_color)

            size = rect.width, 6 * scale
            surface = pygame.surface.Surface(size)

            pos_rect = surface.get_rect()
            pos_rect.topleft = rect.bottomleft
            pos_rect.y += 4

            val_pos = val.get_rect()
            val_pos.center = surface.get_rect().center

            surface.fill(color)

            if is_black_turn:
                val = pygame.transform.flip(val, True, True)
            surface.blit(val, val_pos)
            board_sprite.surface.blit(surface, pos_rect)

            letters_index += 1
