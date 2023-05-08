import string
import typing

import pygame

from chess.notation.algebraic_notation import AlgebraicNotation
from chess.board.side import Side
from chess.notation.forsyth_edwards_notation import FenChars
from chess.asset.asset_manager import AssetManager
from chess.game.game_surface import GameSurface
from config.pg_config import *


class BoardTileIndex(typing.NamedTuple):
    row: int
    col: int
    algebraic_notation: AlgebraicNotation


class RenderPos(typing.NamedTuple):
    x: float
    y: float


class BoardTile:

    @staticmethod
    def get_board_tiles_index(side: Side) -> typing.Generator[BoardTileIndex, None, None]:
        files = string.ascii_lowercase[:BOARD_SIZE]
        files = files[::-1] if side is Side.BLACK else files
        for rank in range(BOARD_SIZE):
            for col, file in enumerate(files):
                str_rank = str(BOARD_SIZE - rank) if side is Side.WHITE else str(rank + 1)
                yield BoardTileIndex(rank, col, AlgebraicNotation(file, str_rank))

    def __init__(
            self,
            rect: pygame.rect.Rect,
            algebraic_notation: AlgebraicNotation,
            fen_val: str = FenChars.BLANK_PIECE
    ):
        self.rect: pygame.rect.Rect = rect
        self.algebraic_notation: AlgebraicNotation = algebraic_notation
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

    def get_picked_up_piece_render_pos(self, piece_surface: pygame.surface.Surface, offset: pygame.math.Vector2) \
            -> RenderPos:
        piece_rect = piece_surface.get_rect(topleft=self.rect.topleft)
        piece_rect.midbottom = pygame.mouse.get_pos()
        pos = pygame.math.Vector2(piece_rect.x, piece_rect.y) - offset
        return RenderPos(pos.x, pos.y)

    def render(self, board_pos: tuple[int, int]) -> None:
        offset = pygame.math.Vector2(board_pos)
        piece_surface = AssetManager.get_piece_surface(self.fen_val)
        piece_pos: RenderPos = BoardTile.get_piece_render_pos(self, offset, piece_surface)
        GameSurface.get().blit(piece_surface, (piece_pos.x, piece_pos.y))
