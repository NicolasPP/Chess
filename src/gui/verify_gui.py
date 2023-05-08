import pygame

from gui.button_gui import ButtonGui
from chess.game.game_surface import GameSurface
from chess.game.game_size import GameSize
from chess.asset.asset_manager import AssetManager
from config.pg_config import *


class VerifyGui:
    def __init__(self, board_rect: pygame.rect.Rect):
        self.board_rect: pygame.rect.Rect = board_rect
        self.bg_surface: pygame.surface.Surface = pygame.surface.Surface(
            (GameSize.get_relative_size(POP_UP_BG_WIDTH), GameSize.get_relative_size(POP_UP_BG_HEIGHT))
        )
        self.bg_surface.fill(AssetManager.get_theme().secondary_light)
        self.bg_surface.set_alpha(VERIFY_BG_ALPHA)
        self.bg_rect: pygame.rect.Rect = self.bg_surface.get_rect(center=board_rect.center)

        self.yes: ButtonGui = ButtonGui(
            int(GameSize.get_relative_size(VERIFY_BUTTON_WIDTH)),
            int(GameSize.get_relative_size(VERIFY_BUTTON_HEIGHT)),
            AssetManager.get_theme().secondary_light)
        self.no: ButtonGui = ButtonGui(
            int(GameSize.get_relative_size(VERIFY_BUTTON_WIDTH)),
            int(GameSize.get_relative_size(VERIFY_BUTTON_HEIGHT)),
            AssetManager.get_theme().secondary_light)
        self.description: ButtonGui = ButtonGui(
            int(GameSize.get_relative_size(POP_UP_BG_WIDTH)),
            int(GameSize.get_relative_size(DESCRIPTION_BUTTON_HEIGHT)),
            AssetManager.get_theme().secondary_light)
        self.action: ButtonGui = ButtonGui(
            int(GameSize.get_relative_size(POP_UP_BG_WIDTH)),
            int(GameSize.get_relative_size(DESCRIPTION_BUTTON_HEIGHT)),
            AssetManager.get_theme().secondary_light)

        self.yes.set_font(
            FONT_FILE,
            int(GameSize.get_relative_size(POP_UP_FONT_SIZE)),
            False,
            AssetManager.get_theme().secondary_dark)
        self.no.set_font(
            FONT_FILE,
            int(GameSize.get_relative_size(POP_UP_FONT_SIZE)),
            False,
            AssetManager.get_theme().secondary_dark)
        self.description.set_font(
            FONT_FILE,
            int(GameSize.get_relative_size(DESCRIPTION_FONT_SIZE)),
            False,
            AssetManager.get_theme().secondary_dark)
        self.action.set_font(
            FONT_FILE,
            int(GameSize.get_relative_size(DESCRIPTION_FONT_SIZE)),
            False,
            AssetManager.get_theme().secondary_dark)

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

    def render(self, game_offset: pygame.rect.Rect) -> None:
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
        self.description.rect.y -= (self.description.rect.height + POP_UP_SPACING)

        self.action.rect.topleft = self.description.rect.bottomleft

        self.yes.rect.center = self.board_rect.center
        self.no.rect.center = self.board_rect.center

        self.yes.rect.x += (self.yes.rect.width // 2) + POP_UP_SPACING
        self.no.rect.x -= (self.no.rect.width // 2) + POP_UP_SPACING

        self.yes.rect.y = self.action.rect.bottom + POP_UP_SPACING
        self.no.rect.y = self.action.rect.bottom + POP_UP_SPACING

    def handle_response(self, game_offset: pygame.rect.Rect) -> None:
        mouse_pos = pygame.math.Vector2(pygame.mouse.get_pos()) - pygame.math.Vector2(game_offset.topleft)
        if self.yes.rect.collidepoint(mouse_pos.x, mouse_pos.y):
            self.set_result(True)

        elif self.no.rect.collidepoint(mouse_pos.x, mouse_pos.y):
            self.set_result(False)

        else:
            self.set_result(False)
