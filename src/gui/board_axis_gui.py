import pygame
import typing

from chess.board.side import Side
from chess.asset.asset_manager import AssetManager
from chess.game.game_surface import GameSurface
from chess.game.game_surface import GameSize
from chess.board.board_tile import BoardTile
from config import *


class TileHover(typing.NamedTuple):
    file: str
    rank: str


class AxisSurfaces(typing.NamedTuple):
    x_axis_surface: pygame.surface.Surface
    y_axis_surface: pygame.surface.Surface


class AxisPos(typing.NamedTuple):
    x_axis_pos: pygame.rect.Rect
    y_axis_pos: pygame.rect.Rect


class AxisGrids(typing.NamedTuple):
    x_axis: list[pygame.rect.Rect]
    y_axis: list[pygame.rect.Rect]


class AxisRects(typing.NamedTuple):
    x_axis: pygame.rect.Rect
    y_axis: pygame.rect.Rect


class BoardAxisGui:

    @staticmethod
    def get_font() -> pygame.font.Font:
        return pygame.font.Font(FONT_FILE, int(GameSize.get_relative_size(AXIS_FONT_SIZE)))

    @staticmethod
    def calculate_axis_rects() -> AxisRects:
        default_pos: tuple[int, int] = 0, 0
        scale = GameSize.get_scale()
        x_axis_rect = pygame.rect.Rect(default_pos, (SQUARE_SIZE * scale * BOARD_SIZE, X_AXIS_HEIGHT * scale))
        y_axis_rect = pygame.rect.Rect(default_pos, (Y_AXIS_WIDTH * scale, SQUARE_SIZE * scale * BOARD_SIZE))
        return AxisRects(x_axis_rect, y_axis_rect)

    @staticmethod
    def create_surfaces() -> AxisSurfaces:
        axis_rects: AxisRects = BoardAxisGui.calculate_axis_rects()
        x_axis_surface = pygame.surface.Surface(axis_rects.x_axis.size)
        y_axis_surface = pygame.surface.Surface(axis_rects.y_axis.size)
        x_axis_surface.fill(AssetManager.get_theme().primary_dark)
        y_axis_surface.fill(AssetManager.get_theme().primary_dark)
        return AxisSurfaces(x_axis_surface, y_axis_surface)

    @staticmethod
    def create_axis() -> AxisGrids:
        x_axis_grid: list[pygame.rect.Rect] = []
        current_pos: pygame.math.Vector2 = pygame.math.Vector2(0)
        size = SQUARE_SIZE * GameSize.get_scale(), SQUARE_SIZE * GameSize.get_scale()
        for col in range(BOARD_SIZE):
            current_pos.x = col * size[0]
            x_axis_grid.append(pygame.rect.Rect((current_pos.x, current_pos.y), size))

        y_axis_grid: list[pygame.rect.Rect] = []
        current_pos = pygame.math.Vector2(0)
        for row in range(BOARD_SIZE):
            current_pos.y = row * size[1]
            y_axis_grid.append(pygame.rect.Rect((current_pos.x, current_pos.y), size))

        return AxisGrids(x_axis_grid, y_axis_grid)

    @staticmethod
    def create_values_dict() -> dict[str, pygame.surface.Surface]:
        values_dict: dict[str, pygame.surface.Surface] = {}
        anti_alias: bool = False
        font = BoardAxisGui.get_font()
        for rank, file in enumerate(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']):
            values_dict[str(rank + 1)] = font.render(str(rank + 1), anti_alias, AssetManager.get_theme().primary_light)
            values_dict[file] = font.render(file, anti_alias, AssetManager.get_theme().primary_light)
        return values_dict

    def __init__(self, board_pos: pygame.rect.Rect, side: Side) -> None:
        self.board_pos: pygame.rect.Rect = board_pos
        self.side: Side = side
        self.axis_surfaces: AxisSurfaces = BoardAxisGui.create_surfaces()
        self.axis: AxisGrids = BoardAxisGui.create_axis()
        self.axis_pos: AxisPos = self.calculate_pos()
        self.values_render_dict: dict[str, pygame.surface.Surface] = BoardAxisGui.create_values_dict()
        self.update_surfaces()
        self.prev_hover: TileHover | None = None

    def calculate_pos(self) -> AxisPos:
        x_axis_rect = self.axis_surfaces.x_axis_surface.get_rect()
        x_axis_rect.topleft = self.board_pos.bottomleft
        y_axis_rect = self.axis_surfaces.y_axis_surface.get_rect()
        y_axis_rect.topright = self.board_pos.topleft
        x_axis_rect.x += BOARD_OUTLINE_THICKNESS
        y_axis_rect.y += BOARD_OUTLINE_THICKNESS
        return AxisPos(x_axis_rect, y_axis_rect)

    def update_surfaces(self) -> None:
        letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        if self.side is Side.BLACK: letters = letters[::-1]
        for rect, file in zip(self.axis.x_axis, letters):
            file_render = self.values_render_dict[file]
            self.axis_surfaces.x_axis_surface.blit(
                file_render, file_render.get_rect(centerx=rect.centerx))

        for index, rect in enumerate(self.axis.y_axis):
            value = str(index + 1) if self.side is Side.BLACK else str(BOARD_SIZE - index)
            rank_render = self.values_render_dict[value]
            self.axis_surfaces.y_axis_surface.blit(
                rank_render, rank_render.get_rect(centery=rect.centery))

    def update_axis_val_render(self, tile_hover: TileHover | None, render_color: tuple[int, int, int]) -> None:
        if tile_hover is None:
            self.reset_hover()
            return
        self.values_render_dict[tile_hover.rank] = BoardAxisGui.get_font().render(
            tile_hover.rank,
            False,
            render_color
        )
        self.values_render_dict[tile_hover.file] = BoardAxisGui.get_font().render(
            tile_hover.file,
            False,
            render_color
        )
        self.update_surfaces()

    def reset_hover(self) -> None:
        self.values_render_dict = BoardAxisGui.create_values_dict()
        self.update_surfaces()

    def update_hover_highlight(self, tile: BoardTile | None) -> None:
        if tile is None:
            if self.prev_hover is not None:
                self.prev_hover = None
                self.reset_hover()
            return
        current_hover: TileHover = TileHover(*tile.algebraic_notation.coordinates)
        if self.prev_hover is None:
            self.prev_hover = current_hover
        else:
            if self.prev_hover == current_hover:
                return
        self.update_axis_val_render(self.prev_hover, AssetManager.get_theme().primary_light)
        self.update_axis_val_render(current_hover, POP_UP_FONT_COLOR)
        self.prev_hover = current_hover

    def render(self) -> None:
        GameSurface.get().blit(self.axis_surfaces.x_axis_surface, self.axis_pos.x_axis_pos)
        GameSurface.get().blit(self.axis_surfaces.y_axis_surface, self.axis_pos.y_axis_pos)
