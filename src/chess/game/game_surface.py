import pygame

from chess.asset.asset_manager import AssetManager
from chess.game.game_size import GameSize


class GameSurface:
    surface: pygame.surface.Surface | None = None

    @staticmethod
    def get() -> pygame.surface.Surface:
        if GameSurface.surface is None:
            raise Exception('surface not created')

        return GameSurface.surface

    @staticmethod
    def create_surface() -> None:
        GameSurface.surface = pygame.surface.Surface(
            (GameSize.get_width(), GameSize.get_height())
        )
        GameSurface.surface.fill(AssetManager.get_theme().dark_color)


