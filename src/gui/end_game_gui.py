import pygame

from chess.asset.asset_manager import AssetManager
from chess.game.game_size import GameSize
from config.pg_config import BOARD_OUTLINE_THICKNESS
from config.pg_config import FONT_FILE
from config.pg_config import OFFER_DRAW_FONT_SIZE
from config.pg_config import OFFER_DRAW_LABEL
from config.pg_config import RESIGN_FONT_SIZE
from config.pg_config import RESIGN_LABEL
from config.pg_config import SQUARE_SIZE
from gui.button_gui import ButtonGui
from gui.game_over_gui import GameOverGui


class EndGameGui:
    @staticmethod
    def calculate_end_game_rect() -> pygame.rect.Rect:
        default_pos: tuple[int, int] = 0, 0
        return pygame.rect.Rect(
            default_pos,
            ((SQUARE_SIZE * GameSize.get_scale() * 2) + (BOARD_OUTLINE_THICKNESS * 2),
             SQUARE_SIZE * GameSize.get_scale() * 1/2))

    def __init__(self, board_rect: pygame.rect.Rect):
        self.board_rect: pygame.rect.Rect = board_rect
        rect: pygame.rect.Rect = EndGameGui.calculate_end_game_rect()
        self.offer_draw: ButtonGui = ButtonGui(rect.width, rect.height, AssetManager.get_theme().primary_dark)
        self.resign: ButtonGui = ButtonGui(rect.width, rect.height, AssetManager.get_theme().primary_dark)
        self.game_over_gui: GameOverGui = GameOverGui(AssetManager.get_theme().primary_dark)
        self.button_init()
        self.recalculate_pos()

    def button_init(self) -> None:
        self.offer_draw.set_font(
            FONT_FILE,
            int(GameSize.get_relative_size(OFFER_DRAW_FONT_SIZE)), False, AssetManager.get_theme().primary_light
        )
        self.resign.set_font(
            FONT_FILE,
            int(GameSize.get_relative_size(RESIGN_FONT_SIZE)), False, AssetManager.get_theme().primary_light
        )
        self.offer_draw.set_hover_color(AssetManager.get_theme().primary_light)
        self.resign.set_hover_color(AssetManager.get_theme().primary_light)
        self.offer_draw.set_label(OFFER_DRAW_LABEL)
        self.resign.set_label(RESIGN_LABEL)

    def render(self, game_offset: pygame.rect.Rect) -> None:
        self.offer_draw.render(game_offset)
        self.resign.render(game_offset)

    def recalculate_pos(self) -> None:
        self.offer_draw.rect.bottomleft = self.board_rect.bottomright
        self.resign.rect.bottomleft = self.board_rect.bottomright
        self.resign.rect.y -= self.offer_draw.rect.height
