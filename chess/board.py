from __future__ import annotations

import enum
import string
import typing

import pygame

import utils.algebraic_notation as AN
import utils.Forsyth_Edwards_notation as FEN
import utils.asset as ASSETS
from config import *


# -- Enums --
class SIDE(enum.Enum):
    WHITE = enum.auto()
    BLACK = enum.auto()


# -----------


# -- Classes --

class BoardSquare:

    @staticmethod
    def create_board_grid(board_sprite: ASSETS.Sprite, pos_rect: pygame.rect.Rect, side: SIDE) -> list[BoardSquare]:
        grid = []
        size = Board.get_grid_surface_size(board_sprite) / BOARD_SIZE
        board_offset = pygame.math.Vector2(pos_rect.topleft)
        grid_offset = pygame.math.Vector2(GRID_OFFSET) * board_sprite.scale
        for row, col, algebraic_notation in BoardSquare.board_square_info(side):
            pos = pygame.math.Vector2(col * size.x, row * size.y)
            rect = pygame.rect.Rect(pos + board_offset + grid_offset, size)
            grid.append(BoardSquare(rect, algebraic_notation, []))
        if side is SIDE.BLACK: grid = grid[::-1]
        return grid

    @staticmethod
    def board_square_info(side: SIDE) -> typing.Generator[tuple[int, int, AN.AlgebraicNotation], None, None]:
        files = string.ascii_lowercase[:BOARD_SIZE]
        files = files[::-1] if side is SIDE.BLACK else files
        for rank in range(BOARD_SIZE):
            for col, file in enumerate(files):
                str_rank = str(BOARD_SIZE - rank) if side is SIDE.WHITE else str(rank + 1)
                yield rank, col, AN.AlgebraicNotation(file, str_rank)

    def __init__(
            self,
            rect: pygame.rect.Rect,
            algebraic_notation: AN.AlgebraicNotation,
            available_moves: list[int],
            FEN_val: str = FEN.FenChars.BLANK_PIECE.value
    ):
        self.rect = rect
        self.algebraic_notation = algebraic_notation
        self.available_moves = available_moves
        self.FEN_val = FEN_val
        self.picked_up: bool = False

    def get_piece_render_pos(self, board_offset: pygame.math.Vector2,
                             piece_surface: pygame.surface.Surface) -> tuple[float, float]:
        if self.picked_up: return self.get_picked_up_piece_render_pos(piece_surface)
        return self.get_not_picked_up_piece_render_pos(board_offset, piece_surface)

    def get_not_picked_up_piece_render_pos(self, board_offset: pygame.math.Vector2,
                                           piece_surface: pygame.surface.Surface) -> tuple[float, float]:
        piece_rect = piece_surface.get_rect(topleft=self.rect.topleft)
        piece_rect.bottom = self.rect.bottom
        pos = pygame.math.Vector2(piece_rect.x, piece_rect.y) + board_offset
        return pos.x, pos.y

    def get_picked_up_piece_render_pos(self, piece_surface: pygame.surface.Surface) \
            -> tuple[float, float]:
        piece_rect = piece_surface.get_rect(topleft=self.rect.topleft)
        piece_rect.midbottom = pygame.mouse.get_pos()
        return piece_rect.x, piece_rect.y


class Board:

    @staticmethod
    def get_grid_surface_size(board_sprite: ASSETS.Sprite) -> pygame.math.Vector2:
        offset = pygame.math.Vector2(GRID_OFFSET) * board_sprite.scale
        board_size = pygame.math.Vector2(board_sprite.surface.get_size())
        return board_size - (offset * 2)

    def __init__(self, board_asset: ASSETS.Asset, side: SIDE, scale: float):
        self.sprite: ASSETS.Sprite = ASSETS.load_board(board_asset, scale)
        replace_board_axis_vals(self.sprite, scale, side)
        if side is SIDE.BLACK: self.sprite.surface = pygame.transform.flip(self.sprite.surface, True, True)
        self.pos_rect: pygame.rect.Rect = self.sprite.surface.get_rect()
        self.grid: list[BoardSquare] = BoardSquare.create_board_grid(self.sprite, self.pos_rect, side)

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
        if board_square.FEN_val == FEN.FenChars.BLANK_PIECE.value: return
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
            pos = pygame.math.Vector2(board_square.rect.topleft)
            available_surface = pygame.surface.Surface(board_square.rect.size)
            available_surface.fill(AVAILABLE_MOVE_COLOR)
            available_surface.set_alpha(AVAILABLE_ALPHA)
            yield available_surface, board_offset + pos


def replace_board_axis_info(board_sprite: ASSETS.Sprite) -> typing.Generator[tuple[int, pygame.rect.Rect], None, None]:
    size = Board.get_grid_surface_size(board_sprite) / BOARD_SIZE
    board_offset = pygame.math.Vector2(board_sprite.surface.get_rect().topleft)
    grid_offset = pygame.math.Vector2(GRID_OFFSET) * board_sprite.scale

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            index = (row * BOARD_SIZE) + col
            pos = pygame.math.Vector2(col * size.x, row * size.y)
            rect = pygame.rect.Rect(pos + board_offset + grid_offset, size)
            yield index, rect


def replace_board_axis_vals(board_sprite: ASSETS.Sprite, scale: float, side: SIDE) -> None:
    nums = list(range(8, 0, -1))
    nums_index = 0
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    letters_index = 0
    color = board_sprite.surface.get_at((0, 0))
    font = pygame.font.Font("assets/fonts/Oleaguid.ttf", 25)
    is_black_turn = True if side is SIDE.BLACK else False

    for index, rect in replace_board_axis_info(board_sprite):
        if index % 8 == 0:
            val = font.render(str(nums[nums_index]), False, (255, 255, 255))

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
            val = font.render(letters[letters_index], False, (255, 255, 255))

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
