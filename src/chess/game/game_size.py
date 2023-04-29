import pygame

from config import DEFAULT_SCALE


class GameSize:
    width: int | None = None
    height: int | None = None
    scale: float | None = None

    @staticmethod
    def get_width() -> int:
        if GameSize.width is None:
            raise Exception('width has not been set')
        return GameSize.width

    @staticmethod
    def get_height() -> int:
        if GameSize.height is None:
            raise Exception('height has not been set')
        return GameSize.height

    @staticmethod
    def set_height(height: int) -> None:
        if height == 0: raise Exception('height cannot be 0')
        if height < 0: raise Exception('height cannot be smaller than 0')
        GameSize.height = height

    @staticmethod
    def set_width(width: int) -> None:
        if width == 0: raise Exception('width cannot be 0')
        if width < 0: raise Exception('width cannot be smaller than 0')
        GameSize.width = width

    @staticmethod
    def add_rects_height(*rects: pygame.rect.Rect) -> None:
        for rect in rects:
            if GameSize.height is None:
                GameSize.set_height(rect.height)
            else:
                GameSize.set_height(GameSize.get_height() + rect.height)

    @staticmethod
    def add_rects_width(*rects: pygame.rect.Rect) -> None:
        for rect in rects:
            if GameSize.width is None:
                GameSize.set_width(rect.width)
            else:
                GameSize.set_width(GameSize.get_width() + rect.width)

    @staticmethod
    def get_scale() -> float:
        if GameSize.scale is None: raise Exception('scale not loaded')
        return GameSize.scale

    @staticmethod
    def load_scale(scale: float) -> None:
        GameSize.scale = scale

    @staticmethod
    def get_relative_size(size: int | float) -> float:
        """
        when designing the gui I picked fixed sizes which looked good on 3.5 scale.
        Instead of implementing a smart way to calculate the size according to the given scale,
        I instead divide it by the default_scale which is 3.5 and then multiply by scale
        """
        return (size * GameSize.get_scale()) / DEFAULT_SCALE

    @staticmethod
    def reset() -> None:
        GameSize.width = GameSize.height = GameSize.scale = None
