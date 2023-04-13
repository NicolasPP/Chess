import typing

import pygame

from chess.asset.asset_manager import AssetManager
from gui.game_over_gui import GameOverGui
from gui.button_gui import ButtonGui
from chess.game.game_size import GameSize

from config import *


class EndGameRects(typing.NamedTuple):
    resign_rect: pygame.rect.Rect
    draw_rect: pygame.rect.Rect


class EndGameGui:
    @staticmethod
    def calculate_end_game_rects() -> EndGameRects:
        default_pos: tuple[int, int] = 0, 0
        resign_rect = pygame.rect.Rect(
            default_pos,
            (GameSize.get_relative_size(RESIGN_BUTTON_WIDTH), GameSize.get_relative_size(RESIGN_BUTTON_HEIGHT)))
        draw_rect = pygame.rect.Rect(
            default_pos,
            (GameSize.get_relative_size(DRAW_BUTTON_WIDTH), GameSize.get_relative_size(DRAW_BUTTON_HEIGHT)))
        return EndGameRects(resign_rect, draw_rect)

    def __init__(self, board_rect: pygame.rect.Rect):
        self.board_rect: pygame.rect.Rect = board_rect
        rects: EndGameRects = EndGameGui.calculate_end_game_rects()
        self.offer_draw: ButtonGui = ButtonGui(
            rects.draw_rect.width, rects.draw_rect.height, AssetManager.get_theme().dark_color)
        self.resign: ButtonGui = ButtonGui(
            rects.resign_rect.width, rects.resign_rect.height, AssetManager.get_theme().dark_color)
        self.game_over_gui: GameOverGui = GameOverGui(AssetManager.get_theme().dark_color)
        self.button_init()
        self.recalculate_pos()

    def button_init(self) -> None:
        self.offer_draw.set_font(
            FONT_FILE,
            int(GameSize.get_relative_size(OFFER_DRAW_FONT_SIZE)), False, AssetManager.get_theme().light_color
        )
        self.resign.set_font(
            FONT_FILE,
            int(GameSize.get_relative_size(RESIGN_FONT_SIZE)), False, AssetManager.get_theme().light_color
        )
        self.offer_draw.set_label(OFFER_DRAW_LABEL)
        self.resign.set_label(RESIGN_LABEL)

    def render(self, game_offset: pygame.math.Vector2) -> None:
        self.offer_draw.render(game_offset)
        self.resign.render(game_offset)

    def recalculate_pos(self) -> None:
        self.offer_draw.rect.bottomleft = self.board_rect.bottomright
        self.resign.rect.bottomleft = self.board_rect.bottomright

        self.offer_draw.rect.x += END_GAME_GUI_SPACING
        self.resign.rect.x += END_GAME_GUI_SPACING

        self.resign.rect.y -= (self.offer_draw.rect.height + END_GAME_GUI_SPACING)
