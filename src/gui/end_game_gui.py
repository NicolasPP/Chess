import typing

import pygame

from chess.asset.asset_manager import AssetManager
from gui.game_over_gui import GameOverGui
from gui.button_gui import ButtonGui

from config import *


class EndGameRects(typing.NamedTuple):
    resign_rect: pygame.rect.Rect
    draw_rect: pygame.rect.Rect


class EndGameGui:
    # FIXME: the size of the font should be as big as possible to fit inside the provided square
    # FIXME: size of the buttons should be reacting to scale not the font size
    # FIXME: scale needs to stop affecting fontsize

    @staticmethod
    def calculate_end_game_rects() -> EndGameRects:
        default_pos: tuple[int, int] = 0, 0
        resign_rect = pygame.rect.Rect(default_pos, (RESIGN_BUTTON_WIDTH, RESIGN_BUTTON_HEIGHT))
        draw_rect = pygame.rect.Rect(default_pos, (DRAW_BUTTON_WIDTH, DRAW_BUTTON_HEIGHT))
        return EndGameRects(resign_rect, draw_rect)

    def __init__(self, board_rect: pygame.rect.Rect):
        self.board_rect: pygame.rect.Rect = board_rect
        self.offer_draw: ButtonGui = ButtonGui(
            DRAW_BUTTON_WIDTH, DRAW_BUTTON_HEIGHT, AssetManager.get_theme().dark_color)
        self.resign: ButtonGui = ButtonGui(
            RESIGN_BUTTON_WIDTH, RESIGN_BUTTON_HEIGHT, AssetManager.get_theme().dark_color)
        self.game_over_gui: GameOverGui = GameOverGui(AssetManager.get_theme().dark_color)
        self.button_init()
        self.recalculate_pos()

    def button_init(self) -> None:
        self.offer_draw.set_font(
            FONT_FILE,
            int((OFFER_DRAW_FONT_SIZE * SCALE) / DEFAULT_FONT_SCALE), False, AssetManager.get_theme().light_color
        )
        self.resign.set_font(
            FONT_FILE,
            int((RESIGN_FONT_SIZE * SCALE) / DEFAULT_FONT_SCALE), False, AssetManager.get_theme().light_color
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
