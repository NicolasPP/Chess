import pygame
from gui.button_gui import ButtonGui

from config import *


class EndGameGui:
    def __init__(self, board_rect: pygame.rect.Rect, bg_color: tuple[int, int, int], fg_color: tuple[int, int, int]):
        self.board_rect = board_rect
        self.offer_draw = ButtonGui(DRAW_BUTTON_WIDTH, DRAW_BUTTON_HEIGHT, bg_color)
        self.resign = ButtonGui(RESIGN_BUTTON_WIDTH, RESIGN_BUTTON_HEIGHT, bg_color)
        self.bg_color: tuple[int, int, int] = bg_color
        self.fg_color: tuple[int, int, int] = fg_color

        # setting up buttons
        self.offer_draw.set_font(FONT_FILE, OFFER_DRAW_FONT_SIZE, False, fg_color)
        self.resign.set_font(FONT_FILE, RESIGN_FONT_SIZE, False, fg_color)
        self.offer_draw.set_label(OFFER_DRAW_LABEL)
        self.resign.set_label(RESIGN_LABEL)

    def render(self) -> None:
        self.offer_draw.render()
        self.resign.render()

    def update(self) -> None: pass

    def recalculate_pos(self) -> None:
        self.offer_draw.rect.bottomleft = self.board_rect.bottomright
        self.resign.rect.bottomleft = self.board_rect.bottomright

        self.offer_draw.rect.x += END_GAME_GUI_SPACING
        self.resign.rect.x += END_GAME_GUI_SPACING

        self.resign.rect.y -= (self.offer_draw.rect.height + END_GAME_GUI_SPACING)
