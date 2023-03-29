import pygame

from config import GAME_OVER_ALPHA, GAME_OVER_COLOR, OPAQUE


class GameOverGui:
    def __init__(self, bg_color: tuple[int, int, int]):
        self.final_frame: pygame.surfac.Surface = pygame.surface.Surface(pygame.display.get_surface().get_size())
        self.final_frame.set_alpha(OPAQUE)
        self.game_over_surface: pygame.surface.Surface = pygame.surface.Surface(pygame.display.get_surface().get_size())
        self.game_over_surface.set_alpha(GAME_OVER_ALPHA)
        self.bg_color: tuple[int, int, int] = bg_color

    def set_final_frame(self) -> None:
        self.final_frame.blit(pygame.display.get_surface(), (0, 0))
        self.game_over_surface.fill(GAME_OVER_COLOR)
        self.final_frame.blit(self.game_over_surface, (0, 0))

    def render(self) -> None:
        pygame.display.get_surface().fill(self.bg_color)
        pygame.display.get_surface().blit(self.final_frame, (0, 0))
