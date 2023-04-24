import typing

import pygame

from chess.notation.algebraic_notation import AlgebraicNotation
from chess.notation.portable_game_notation import generate_move_text
from chess.notation.forsyth_edwards_notation import Fen
from chess.game.game_surface import GameSurface
from chess.asset.asset_manager import AssetManager
from chess.game.game_size import GameSize

from config import *


class PlayedMovesSurfaces(typing.NamedTuple):
    background: pygame.surface.Surface


class PlayedMovesGui:

    @staticmethod
    def calculate_background_rect() -> pygame.rect.Rect:
        return pygame.rect.Rect(
            0, 0,
            SQUARE_SIZE * GameSize.get_scale() * 2,
            SQUARE_SIZE * GameSize.get_scale() * (BOARD_SIZE - 1)
        )

    @staticmethod
    def create_played_moves_surfaces(background_rect: pygame.rect.Rect) -> PlayedMovesSurfaces:
        background_surface = pygame.surface.Surface(background_rect.size)
        background_surface.fill(AssetManager.get_theme().light_color)
        return PlayedMovesSurfaces(background_surface)

    def __init__(self, board_rect: pygame.rect.Rect) -> None:
        self.played_moves: list[str] = []
        self.board_rect: pygame.rect.Rect = board_rect
        self.background_rect: pygame.rect.Rect = PlayedMovesGui.calculate_background_rect()
        self.played_surfaces: PlayedMovesSurfaces = PlayedMovesGui.create_played_moves_surfaces(self.background_rect)
        self.calculate_pos()

    def add_played_move(self, from_index: int, dest_index: int, fen: Fen, target_fen: str) -> None:
        from_an = AlgebraicNotation.get_an_from_index(from_index)
        dest_an = AlgebraicNotation.get_an_from_index(dest_index)
        move = generate_move_text(fen, from_an, dest_an, target_fen)
        print(move)
        self.played_moves.append(move)

    def calculate_pos(self) -> None:
        self.background_rect.topleft = self.board_rect.topright
        self.background_rect.x += GUI_SPACING

    def render(self) -> None:
        GameSurface.get().blit(self.played_surfaces.background, self.background_rect)
