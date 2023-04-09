import pygame

from chess.game_surface import GameSurface
from config import GAME_OVER_ALPHA, GAME_OVER_COLOR, OPAQUE


class GameOverGui:
    def __init__(self, bg_color: tuple[int, int, int]):
        self.final_frame: pygame.surfac.Surface = pygame.surface.Surface(GameSurface.get().get_size())
        self.final_frame.set_alpha(OPAQUE)
        self.game_over_surface: pygame.surface.Surface = pygame.surface.Surface(GameSurface.get().get_size())
        self.game_over_surface.set_alpha(GAME_OVER_ALPHA)
        self.bg_color: tuple[int, int, int] = bg_color

    def set_final_frame(self) -> None:
        self.final_frame.blit(GameSurface.get(), (0, 0))
        self.game_over_surface.fill(GAME_OVER_COLOR)
        self.final_frame.blit(self.game_over_surface, (0, 0))

    def render(self) -> None:
        GameSurface.get().fill(self.bg_color)
        GameSurface.get().blit(self.final_frame, (0, 0))
