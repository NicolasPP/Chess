import pygame

from chess.asset.asset_manager import AssetManager

class GameSurface:
    surface: pygame.surface.Surface | None = None
    width: int | None = None
    height: int | None = None

    @staticmethod
    def get() -> pygame.surface.Surface:
        if GameSurface.surface is None:
            raise Exception('surface not created')

        return GameSurface.surface

    @staticmethod
    def create_surface() -> None:
        GameSurface.surface = pygame.surface.Surface(
            (GameSurface.get_width(), GameSurface.get_height())
        )
        GameSurface.surface.fill(AssetManager.get_theme().dark_color)

    @staticmethod
    def get_width() -> int:
        if GameSurface.width is None:
            raise Exception('width has not been set')
        return GameSurface.width

    @staticmethod
    def get_height() -> int:
        if GameSurface.height is None:
            raise Exception('height has not been set')
        return GameSurface.height

    @staticmethod
    def set_height(height: int) -> None:
        if height == 0: raise Exception('height cannot be 0')
        if height < 0: raise Exception('height cannot be smaller than 0')
        GameSurface.height = height

    @staticmethod
    def set_width(width: int) -> None:
        if width == 0: raise Exception('width cannot be 0')
        if width < 0: raise Exception('width cannot be smaller than 0')
        GameSurface.width = width

    @staticmethod
    def add_rects_height(*rects: pygame.rect.Rect) -> None:
        for rect in rects:
            if GameSurface.height is None:
                GameSurface.set_height(rect.height)
            else:
                GameSurface.set_height(GameSurface.get_height() + rect.height)

    @staticmethod
    def add_rects_width(*rects: pygame.rect.Rect) -> None:
        for rect in rects:
            if GameSurface.width is None:
                GameSurface.set_width(rect.width)
            else:
                GameSurface.set_width(GameSurface.get_width() + rect.width)
