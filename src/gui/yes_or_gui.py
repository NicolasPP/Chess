import pygame

from gui.button_gui import ButtonGui

from config import *

# TODO: center the buttons
# TODO: add background
# TODO: add boarder
# TODO: add description


class YesOrNoGui:
    def __init__(self, board_rect: pygame.rect.Rect):
        self.board_rect: pygame.rect.Rect = board_rect
        self.yes: ButtonGui = ButtonGui(DRAW_BUTTON_WIDTH, DRAW_BUTTON_HEIGHT, AVAILABLE_MOVE_COLOR)
        self.no: ButtonGui = ButtonGui(RESIGN_BUTTON_WIDTH, RESIGN_BUTTON_HEIGHT, (255, 255, 255))
        self.result: bool | None = None

    def render(self) -> None:
        self.yes.render()
        self.no.render()

    def set_result(self, result: bool | None) -> None:
        self.result = result

    def recalculate_pos(self) -> None:
        self.yes.rect.x += 100
