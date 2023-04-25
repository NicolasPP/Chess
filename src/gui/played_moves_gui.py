import dataclasses

import pygame

from chess.notation.algebraic_notation import AlgebraicNotation
from chess.notation.portable_game_notation import generate_move_text
from chess.notation.forsyth_edwards_notation import Fen
from chess.game.game_surface import GameSurface
from chess.asset.asset_manager import AssetManager
from chess.game.game_size import GameSize

from config import *


@dataclasses.dataclass
class PlayedMovesSurfaces:
    background: pygame.surface.Surface
    scroll: pygame.surface.Surface
    scroll_window: pygame.surface.Surface


class PlayedMovesGui:

    @staticmethod
    def create_move_cell_surface(move: str) -> pygame.surface.Surface:
        cell_surface: pygame.surface.Surface = pygame.surface.Surface(PlayedMovesGui.get_move_cell_size())
        move_render = PlayedMovesGui.get_font().render(move, False, AssetManager.get_theme().primary_light)
        cell_surface.fill(AssetManager.get_theme().primary_dark)
        cell_surface.blit(move_render, move_render.get_rect(center=cell_surface.get_rect().center))
        return cell_surface

    @staticmethod
    def get_move_cell_size() -> tuple[int, int]:
        width: int = int(SQUARE_SIZE * GameSize.get_scale())
        height: int = int(SQUARE_SIZE * GameSize.get_scale() * 1 / 2)
        return width, height

    @staticmethod
    def get_font() -> pygame.font.Font:
        return pygame.font.Font(FONT_FILE, int(GameSize.get_relative_size(PLAYED_MOVE_FONT_SIZE)))

    @staticmethod
    def calculate_background_rect() -> pygame.rect.Rect:
        return pygame.rect.Rect(
            (0, 0),
            ((SQUARE_SIZE * GameSize.get_scale() * 2) + (BOARD_OUTLINE_THICKNESS * 2),
             (SQUARE_SIZE * GameSize.get_scale() * (BOARD_SIZE - 1)) + (BOARD_OUTLINE_THICKNESS * 2))
        )

    @staticmethod
    def create_played_moves_surfaces(background_rect: pygame.rect.Rect) -> PlayedMovesSurfaces:
        background_surface = pygame.surface.Surface(background_rect.size)
        background_surface.fill(AssetManager.get_theme().primary_light)
        scroll_window_surface: pygame.surface.Surface = pygame.surface.Surface(
            (background_rect.width - BOARD_OUTLINE_THICKNESS,
             background_rect.height - (BOARD_OUTLINE_THICKNESS * 2))
        )
        scroll_surface: pygame.surface.Surface = pygame.surface.Surface(
            scroll_window_surface.get_size()
        )
        scroll_surface.fill(AssetManager.get_theme().primary_dark)
        background_surface.blit(scroll_surface, (0, BOARD_OUTLINE_THICKNESS))
        return PlayedMovesSurfaces(background_surface, scroll_surface, scroll_window_surface)

    def __init__(self, board_rect: pygame.rect.Rect) -> None:
        self.moves: list[str] = []
        self.board_rect: pygame.rect.Rect = board_rect
        self.background_rect: pygame.rect.Rect = PlayedMovesGui.calculate_background_rect()
        self.played_surfaces: PlayedMovesSurfaces = PlayedMovesGui.create_played_moves_surfaces(self.background_rect)
        self.cell_pos: pygame.math.Vector2 = pygame.math.Vector2(0)
        self.scroll_pos: pygame.math.Vector2 = pygame.math.Vector2(0)
        self.calculate_pos()

    def add_played_move(self, from_index: int, dest_index: int, fen: Fen, target_fen: str) -> None:
        from_an = AlgebraicNotation.get_an_from_index(from_index)
        dest_an = AlgebraicNotation.get_an_from_index(dest_index)
        move: str = generate_move_text(fen, from_an, dest_an, target_fen)
        self.update_scroll_surface(move)
        self.moves.append(move)

    def recalculate_scroll_size(self, move_surface: pygame.surface.Surface) -> None:
        if self.cell_pos.y < self.played_surfaces.scroll.get_height(): return
        new_surface = pygame.surface.Surface(
            (self.played_surfaces.scroll.get_width(),
             self.played_surfaces.scroll.get_height() + move_surface.get_rect().height))
        new_surface.fill(AssetManager.get_theme().primary_dark)
        new_surface.blit(self.played_surfaces.scroll, (0, 0))
        self.played_surfaces.scroll = new_surface

    def update_scroll_surface(self, move: str) -> None:
        move_surface = PlayedMovesGui.create_move_cell_surface(move)

        self.recalculate_scroll_size(move_surface)

        self.played_surfaces.scroll.blit(move_surface, self.cell_pos)
        if len(self.moves) % 2 == 0:
            self.cell_pos.x += (move_surface.get_rect().width + BOARD_OUTLINE_THICKNESS)
        else:
            self.cell_pos.x -= (move_surface.get_rect().width + BOARD_OUTLINE_THICKNESS)
            self.cell_pos.y += move_surface.get_rect().height
        diff = self.played_surfaces.scroll_window.get_height() - self.played_surfaces.scroll.get_height()
        self.scroll_pos.y = diff
        self.update_background_surface()

    def update_background_surface(self) -> None:
        self.played_surfaces.scroll_window.blit(self.played_surfaces.scroll, self.scroll_pos)
        self.played_surfaces.background.blit(self.played_surfaces.scroll_window, (0, BOARD_OUTLINE_THICKNESS))

    def calculate_pos(self) -> None:
        self.background_rect.topleft = self.board_rect.topright

    def render(self) -> None:
        GameSurface.get().blit(self.played_surfaces.background, self.background_rect)

    def scroll_down(self, game_offset: pygame.rect.Rect) -> None:
        mouse_pos = pygame.math.Vector2(pygame.mouse.get_pos()) - pygame.math.Vector2(game_offset.topleft)
        if not self.background_rect.collidepoint((mouse_pos.x, mouse_pos.y)):
            return
        if self.played_surfaces.scroll.get_size() == self.played_surfaces.scroll_window.get_size():
            return
        diff = self.played_surfaces.scroll_window.get_height() - self.played_surfaces.scroll.get_height()
        if self.scroll_pos.y <= diff:
            self.scroll_pos.y = diff
            return
        self.scroll_pos.y -= SCROLL_SPEED
        self.update_background_surface()

    def scroll_up(self, game_offset: pygame.rect.Rect) -> None:
        mouse_pos = pygame.math.Vector2(pygame.mouse.get_pos()) - pygame.math.Vector2(game_offset.topleft)
        if not self.background_rect.collidepoint((mouse_pos.x, mouse_pos.y)):
            return
        if self.played_surfaces.scroll.get_size() == self.played_surfaces.scroll_window.get_size():
            return
        if self.scroll_pos.y >= 0:
            self.scroll_pos.y = 0
            return
        self.scroll_pos.y += SCROLL_SPEED
        self.update_background_surface()
