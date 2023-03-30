import pygame

from gui.button_gui import ButtonGui

from config import *


class YesOrNoGui:
    def __init__(self, board_rect: pygame.rect.Rect):
        self.board_rect: pygame.rect.Rect = board_rect
        self.bg_surface: pygame.surface.Surface = pygame.surface.Surface(YES_OR_NO_BG_SIZE)
        self.bg_surface.fill(YES_OR_NO_BG_COLOR)
        self.bg_surface.set_alpha(YES_OR_NO_BG_ALPHA)
        self.bg_rect: pygame.rect.Rect = self.bg_surface.get_rect(center=board_rect.center)

        self.yes: ButtonGui = ButtonGui(DRAW_BUTTON_WIDTH, DRAW_BUTTON_HEIGHT, YES_OR_NO_BG_COLOR)
        self.no: ButtonGui = ButtonGui(RESIGN_BUTTON_WIDTH, RESIGN_BUTTON_HEIGHT, YES_OR_NO_BG_COLOR)
        self.description: ButtonGui = ButtonGui(DESCRIPTION_BUTTON_WIDTH, DESCRIPTION_BUTTON_HEIGHT, YES_OR_NO_BG_COLOR)
        self.action: ButtonGui = ButtonGui(DESCRIPTION_BUTTON_WIDTH, DESCRIPTION_BUTTON_HEIGHT, YES_OR_NO_BG_COLOR)

        self.yes.set_font(FONT_FILE, YES_OR_NO_FONT_SIZE, False, YES_NO_FONT_COLOR)
        self.no.set_font(FONT_FILE, YES_OR_NO_FONT_SIZE, False, YES_NO_FONT_COLOR)
        self.description.set_font(FONT_FILE, DESCRIPTION_FONT_SIZE, False, YES_NO_FONT_COLOR)
        self.action.set_font(FONT_FILE, DESCRIPTION_FONT_SIZE, False, YES_NO_FONT_COLOR)

        self.yes.set_label(YES_LABEL)
        self.no.set_label(NO_LABEL)
        self.description.set_label(DESCRIPTION_LABEL)

        self.description.set_hover(False)
        self.action.set_hover(False)
        self.result: bool | None = None

    def set_action_label(self, label: str) -> None:
        self.action.set_label(label)

    def set_description_label(self, label: str) -> None:
        self.description.set_label(label)

    def render(self) -> None:
        pygame.display.get_surface().blit(self.bg_surface, self.bg_rect)
        self.description.render()
        self.action.render()
        self.yes.render()
        self.no.render()

    def set_result(self, result: bool | None) -> None:
        self.result = result

    def recalculate_pos(self) -> None:
        self.bg_rect = self.bg_surface.get_rect(center=self.board_rect.center)

        self.description.rect.center = self.board_rect.center
        self.description.rect.y -= (self.description.rect.height + YES_OR_NO_SPACING)

        self.action.rect.topleft = self.description.rect.bottomleft

        self.yes.rect.center = self.board_rect.center
        self.no.rect.center = self.board_rect.center

        self.yes.rect.x += (self.yes.rect.width // 2) + YES_OR_NO_SPACING
        self.no.rect.x -= (self.no.rect.width // 2) + YES_OR_NO_SPACING

        self.yes.rect.y = self.action.rect.bottom + YES_OR_NO_SPACING
        self.no.rect.y = self.action.rect.bottom + YES_OR_NO_SPACING
