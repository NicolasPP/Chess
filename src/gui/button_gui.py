import pygame
import dataclasses


@dataclasses.dataclass
class FontRenderInfo:
    font: pygame.font.Font
    anti_alias: bool
    color: tuple[int, int, int]


class ButtonGui:
    def __init__(self, width: int, height: int, bg_color: tuple[int, int, int]):
        self.rect: pygame.rect.Rect = pygame.rect.Rect(0, 0, width, height)
        self.surface: pygame.surface.Surface = pygame.surface.Surface(self.rect.size)
        self.hover_surface: pygame.surface.Surface = pygame.surface.Surface(self.rect.size)
        self.font_info: FontRenderInfo | None = None
        self.surface.fill(bg_color)
        self.hover_surface.fill(bg_color)
        self.hover_surface.set_alpha(70)

    def set_font(self, font_file: str, font_size: int, anti_alias: bool, font_color: tuple[int, int, int]) -> None:
        self.font_info = FontRenderInfo(pygame.font.Font(font_file, font_size), anti_alias, font_color)

    def set_label(self, text: str) -> None:
        if self.font_info is None: raise Exception('Font not initialised')
        label_surface = self.font_info.font.render(text, self.font_info.anti_alias, self.font_info.color)
        label_pos: pygame.rect.Rect = label_surface.get_rect(center=self.rect.center)
        self.surface.blit(label_surface, label_pos)

    def render(self) -> None:
        pygame.display.get_surface().blit(self.surface, self.rect)
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            pygame.display.get_surface().blit(self.hover_surface, self.rect)
