import pygame

from gui.button_gui import ButtonGui
from chess.game.game_surface import GameSurface
from chess.game.game_size import GameSize
from config import *


class VerifyGui:
    def __init__(self, board_rect: pygame.rect.Rect):
        self.board_rect: pygame.rect.Rect = board_rect
        self.bg_surface: pygame.surface.Surface = pygame.surface.Surface(
            (GameSize.get_relative_size(VERIFY_BG_WIDTH), GameSize.get_relative_size(VERIFY_BG_HEIGHT))
        )
        self.bg_surface.fill(VERIFY_BG_COLOR)
        self.bg_surface.set_alpha(VERIFY_BG_ALPHA)
        self.bg_rect: pygame.rect.Rect = self.bg_surface.get_rect(center=board_rect.center)

        self.yes: ButtonGui = ButtonGui(
            int(GameSize.get_relative_size(DRAW_BUTTON_WIDTH)),
            int(GameSize.get_relative_size(DRAW_BUTTON_HEIGHT)),
            VERIFY_BG_COLOR)
        self.no: ButtonGui = ButtonGui(
            int(GameSize.get_relative_size(RESIGN_BUTTON_WIDTH)),
            int(GameSize.get_relative_size(RESIGN_BUTTON_HEIGHT)),
            VERIFY_BG_COLOR)
        self.description: ButtonGui = ButtonGui(
            int(GameSize.get_relative_size(VERIFY_BG_WIDTH)),
            int(GameSize.get_relative_size(DESCRIPTION_BUTTON_HEIGHT)),
            VERIFY_BG_COLOR)
        self.action: ButtonGui = ButtonGui(
            int(GameSize.get_relative_size(VERIFY_BG_WIDTH)),
            int(GameSize.get_relative_size(DESCRIPTION_BUTTON_HEIGHT)),
            VERIFY_BG_COLOR)

        self.yes.set_font(
            FONT_FILE,
            int(GameSize.get_relative_size(VERIFY_FONT_SIZE)),
            False,
            VERIFY_FONT_COLOR)
        self.no.set_font(
            FONT_FILE,
            int(GameSize.get_relative_size(VERIFY_FONT_SIZE)),
            False,
            VERIFY_FONT_COLOR)
        self.description.set_font(
            FONT_FILE,
            int(GameSize.get_relative_size(DESCRIPTION_FONT_SIZE)),
            False,
            VERIFY_FONT_COLOR)
        self.action.set_font(
            FONT_FILE,
            int(GameSize.get_relative_size(DESCRIPTION_FONT_SIZE)),
            False,
            VERIFY_FONT_COLOR)

        self.yes.set_label(YES_LABEL)
        self.no.set_label(NO_LABEL)
        self.description.set_label(DESCRIPTION_LABEL)

        self.description.set_hover(False)
        self.action.set_hover(False)
        self.result: bool | None = None

        self.recalculate_pos()

    def set_action_label(self, label: str) -> None:
        self.action.set_label(label)

    def set_description_label(self, label: str) -> None:
        self.description.set_label(label)

    def render(self, game_offset: pygame.math.Vector2) -> None:
        GameSurface.get().blit(self.bg_surface, self.bg_rect)
        self.description.render(game_offset)
        self.action.render(game_offset)
        self.yes.render(game_offset)
        self.no.render(game_offset)

    def set_result(self, result: bool | None) -> None:
        self.result = result

    def recalculate_pos(self) -> None:
        self.bg_rect = self.bg_surface.get_rect(center=self.board_rect.center)

        self.description.rect.center = self.board_rect.center
        self.description.rect.y -= (self.description.rect.height + VERIFY_SPACING)

        self.action.rect.topleft = self.description.rect.bottomleft

        self.yes.rect.center = self.board_rect.center
        self.no.rect.center = self.board_rect.center

        self.yes.rect.x += (self.yes.rect.width // 2) + VERIFY_SPACING
        self.no.rect.x -= (self.no.rect.width // 2) + VERIFY_SPACING

        self.yes.rect.y = self.action.rect.bottom + VERIFY_SPACING
        self.no.rect.y = self.action.rect.bottom + VERIFY_SPACING

    def handle_response(self, game_offset: pygame.rect.Rect) -> None:
        mouse_pos = pygame.math.Vector2(pygame.mouse.get_pos()) - pygame.math.Vector2(game_offset.topleft)
        if self.yes.rect.collidepoint(mouse_pos.x, mouse_pos.y):
            self.set_result(True)

        elif self.no.rect.collidepoint(mouse_pos.x, mouse_pos.y):
            self.set_result(False)

        else:
            self.set_result(False)
