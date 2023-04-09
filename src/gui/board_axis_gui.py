import pygame
import typing

from chess.piece_movement import Side
from chess.asset.asset_manager import AssetManager
from chess.game_surface import GameSurface
from config import *


class AxisSurfaces(typing.NamedTuple):
    x_axis_surface: pygame.surface.Surface
    y_axis_surface: pygame.surface.Surface


class AxisPos(typing.NamedTuple):
    x_axis_pos: pygame.rect.Rect
    y_axis_pos: pygame.rect.Rect


class AxisGrids(typing.NamedTuple):
    x_axis_grid: list[pygame.rect.Rect]
    y_axis_grid: list[pygame.rect.Rect]


class AxisRects(typing.NamedTuple):
    x_axis: pygame.rect.Rect
    y_axis: pygame.rect.Rect


# FIXME: Store axis values surfaces better, so I can highlight which col and row the player in hovering over
class BoardAxisGui:

    @staticmethod
    def calculate_axis_rects(scale: float) -> AxisRects:
        default_pos: tuple[int, int] = 0, 0
        x_axis_rect = pygame.rect.Rect(default_pos, (SQUARE_SIZE * scale * BOARD_SIZE, X_AXIS_HEIGHT * scale))
        y_axis_rect = pygame.rect.Rect(default_pos, (Y_AXIS_WIDTH * scale, SQUARE_SIZE * scale * BOARD_SIZE))
        return AxisRects(x_axis_rect, y_axis_rect)

    @staticmethod
    def create_surfaces() -> AxisSurfaces:
        x_axis_surface = pygame.surface.Surface((SQUARE_SIZE * SCALE * BOARD_SIZE, X_AXIS_HEIGHT * SCALE))
        y_axis_surface = pygame.surface.Surface((Y_AXIS_WIDTH * SCALE, SQUARE_SIZE * SCALE * BOARD_SIZE))
        x_axis_surface.fill(AssetManager.get_theme().dark_color)
        y_axis_surface.fill(AssetManager.get_theme().dark_color)
        return AxisSurfaces(x_axis_surface, y_axis_surface)

    @staticmethod
    def create_grids() -> AxisGrids:
        x_axis_grid: list[pygame.rect.Rect] = []
        current_pos: pygame.math.Vector2 = pygame.math.Vector2(0)
        size = SQUARE_SIZE * SCALE, SQUARE_SIZE * SCALE
        for col in range(BOARD_SIZE):
            current_pos.x = col * size[0]
            x_axis_grid.append(pygame.rect.Rect((current_pos.x, current_pos.y), size))

        y_axis_grid: list[pygame.rect.Rect] = []
        current_pos: pygame.math.Vector2 = pygame.math.Vector2(0)
        for row in range(BOARD_SIZE):
            current_pos.y = row * size[1]
            y_axis_grid.append(pygame.rect.Rect((current_pos.x, current_pos.y), size))

        return AxisGrids(x_axis_grid, y_axis_grid)

    def __init__(self, board_pos: pygame.rect.Rect, side: Side) -> None:
        self.board_pos: pygame.rect.Rect = board_pos
        self.side: Side = side
        self.axis_surfaces: AxisSurfaces = BoardAxisGui.create_surfaces()
        self.axis_grids: AxisGrids = BoardAxisGui.create_grids()
        self.axis_pos: AxisPos = self.calculate_pos()
        self.render_values()

    def calculate_pos(self) -> AxisPos:
        x_axis_rect = self.axis_surfaces.x_axis_surface.get_rect()
        x_axis_rect.topleft = self.board_pos.bottomleft
        y_axis_rect = self.axis_surfaces.y_axis_surface.get_rect()
        y_axis_rect.topright = self.board_pos.topleft
        x_axis_rect.x += BOARD_OUTLINE_THICKNESS
        y_axis_rect.y += BOARD_OUTLINE_THICKNESS
        return AxisPos(x_axis_rect, y_axis_rect)

    def render_values(self) -> None:
        anti_alias: bool = False
        font_color: tuple[int, int, int] = 255, 255, 255
        font = pygame.font.Font(FONT_FILE, int((AXIS_FONT_SIZE * SCALE) / DEFAULT_FONT_SCALE))

        for index, rect in enumerate(self.axis_grids.x_axis_grid):
            text_render = font.render(str(index + 1), anti_alias, font_color)
            self.axis_surfaces.x_axis_surface.blit(
                text_render, text_render.get_rect(centerx=rect.centerx))

        letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        for rect, letter in zip(self.axis_grids.y_axis_grid, letters):
            text_render = font.render(letter, anti_alias, font_color)
            self.axis_surfaces.y_axis_surface.blit(
                text_render, text_render.get_rect(centery=rect.centery))

    def render(self) -> None:
        GameSurface.get().blit(self.axis_surfaces.x_axis_surface, self.axis_pos.x_axis_pos)
        GameSurface.get().blit(self.axis_surfaces.y_axis_surface, self.axis_pos.y_axis_pos)
