import typing

import pygame

from chess.board.board_tile import BoardTile
from chess.game.game_surface import GameSurface
from chess.game.game_size import GameSize

from config import *


class PrevMove(typing.NamedTuple):
    from_tile: BoardTile
    dest_tile: BoardTile


class PrevMoveSurfaces(typing.NamedTuple):
    from_surface: pygame.surface.Surface
    dest_surface: pygame.surface.Surface


class PreviousMoveGui:

    @staticmethod
    def get_prev_move_surfaces() -> PrevMoveSurfaces:
        from_surface: pygame.surface.Surface = pygame.surface.Surface(
            (SQUARE_SIZE * GameSize.get_scale(), SQUARE_SIZE * GameSize.get_scale()))
        dest_surface: pygame.surface.Surface = pygame.surface.Surface(
            (SQUARE_SIZE * GameSize.get_scale(), SQUARE_SIZE * GameSize.get_scale()))
        from_surface.fill(POP_UP_FONT_COLOR)
        from_surface.set_alpha(PREV_MOVE_ALPHA)
        dest_surface.fill(POP_UP_FONT_COLOR)
        dest_surface.set_alpha(PREV_MOVE_ALPHA)
        return PrevMoveSurfaces(from_surface, dest_surface)

    def __init__(self, board_rect: pygame.rect.Rect):
        self.board_rect: pygame.rect.Rect = board_rect
        self.prev_move: PrevMove | None = None
        self.prev_move_surfaces: PrevMoveSurfaces = PreviousMoveGui.get_prev_move_surfaces()

    def set_prev_move(self, from_tile: BoardTile, dest_tile: BoardTile) -> None:
        if self.prev_move is None:
            self.prev_move = PrevMove(from_tile, dest_tile)

        else:
            self.prev_move = PrevMove(from_tile, dest_tile)

    def render(self) -> None:
        if self.prev_move is None: return
        board_offset: pygame.math.Vector2 = pygame.math.Vector2(self.board_rect.topleft)
        from_pos: pygame.math.Vector2 = pygame.math.Vector2(self.prev_move.from_tile.rect.topleft) + board_offset
        dest_pos: pygame.math.Vector2 = pygame.math.Vector2(self.prev_move.dest_tile.rect.topleft) + board_offset
        GameSurface.get().blit(self.prev_move_surfaces.from_surface, from_pos)
        GameSurface.get().blit(self.prev_move_surfaces.dest_surface, dest_pos)
