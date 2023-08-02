import dataclasses

import pygame

from chess.game.game_surface import GameSurface
from config.pg_config import HOVER_ALPHA


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
        self.hover: bool = True
        self.bg_color: tuple[int, int, int] = bg_color
        self.font_info: FontRenderInfo | None = None
        self.surface.fill(bg_color)
        self.hover_surface.fill(bg_color)
        self.hover_surface.set_alpha(HOVER_ALPHA)
        self.enabled: bool = True

    def set_enable(self, new_enable: bool) -> None:
        self.enabled = new_enable

    def set_hover_color(self, hover_color: tuple[int, int, int]) -> None:
        self.hover_surface.fill(hover_color)

    def set_font(self, font_file: str, font_size: int, anti_alias: bool, font_color: tuple[int, int, int]) -> None:
        self.font_info = FontRenderInfo(pygame.font.Font(font_file, font_size), anti_alias, font_color)

    def set_label(self, text: str) -> None:
        if self.font_info is None: raise Exception('Font not initialised')
        self.surface.fill(self.bg_color)
        label_surface = self.font_info.font.render(text, self.font_info.anti_alias, self.font_info.color)
        label_pos: pygame.rect.Rect = label_surface.get_rect(center=self.surface.get_rect().center)
        self.surface.blit(label_surface, label_pos)

    def set_hover(self, hover: bool) -> None:
        self.hover = hover

    def render(self, game_offset: pygame.rect.Rect) -> None:
        GameSurface.get().blit(self.surface, self.rect)
        vec_offset: pygame.math.Vector2 = pygame.math.Vector2(game_offset.topleft)
        if not self.hover or not self.enabled: return
        mouse_pos = pygame.math.Vector2(pygame.mouse.get_pos()) - vec_offset
        if self.rect.collidepoint(mouse_pos.x, mouse_pos.y):
            GameSurface.get().blit(self.hover_surface, self.rect)
