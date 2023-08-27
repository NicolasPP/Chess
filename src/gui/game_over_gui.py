import pygame

from chess.asset.asset_manager import AssetManager
from chess.game.chess_match import MatchResult
from chess.game.game_size import GameSize
from chess.game.game_surface import GameSurface
from config.pg_config import DRAW_MESSAGE
from config.pg_config import FONT_FILE
from config.pg_config import GAME_OVER_ALPHA
from config.pg_config import GAME_OVER_COLOR
from config.pg_config import OPAQUE
from config.pg_config import POP_UP_BG_HEIGHT
from config.pg_config import POP_UP_BG_WIDTH
from config.pg_config import POP_UP_FONT_SIZE
from config.pg_config import QUIT_HEIGHT
from config.pg_config import QUIT_LABEL
from config.pg_config import QUIT_WIDTH
from config.pg_config import RESULT_TYPE_FONT_SIZE
from config.pg_config import WINNING_MESSAGE
from gui.button_gui import ButtonGui


class GameOverGui:
    @staticmethod
    def get_font(size: int) -> pygame.font.Font:
        return pygame.font.Font(FONT_FILE, int(GameSize.get_relative_size(size)))

    def __init__(self, bg_color: tuple[int, int, int]):
        self.final_frame: pygame.surface.Surface = pygame.surface.Surface(GameSurface.get().get_size())
        self.final_frame.set_alpha(OPAQUE)
        self.game_over_surface: pygame.surface.Surface = pygame.surface.Surface(GameSurface.get().get_size())
        self.game_result_bg: pygame.surface.Surface = pygame.surface.Surface(
            (GameSize.get_relative_size(POP_UP_BG_WIDTH), GameSize.get_relative_size(POP_UP_BG_HEIGHT))
        )
        self.quit_button: ButtonGui = ButtonGui(
            int(GameSize.get_relative_size(QUIT_WIDTH)),
            int(GameSize.get_relative_size(QUIT_HEIGHT)),
            AssetManager.get_theme().secondary_light
        )
        self.quit_button.set_font(FONT_FILE, POP_UP_FONT_SIZE, False, AssetManager.get_theme().secondary_dark)
        self.quit_button.set_label(QUIT_LABEL)
        self.quit_button.set_hover_color(AssetManager.get_theme().secondary_light)
        self.game_over_surface.set_alpha(GAME_OVER_ALPHA)
        self.game_result_bg.fill(AssetManager.get_theme().secondary_light)
        self.bg_color: tuple[int, int, int] = bg_color

    def set_final_frame(self, game_result: str, result_type: str) -> None:
        self.final_frame.blit(GameSurface.get(), (0, 0))
        self.game_over_surface.fill(GAME_OVER_COLOR)
        self.final_frame.blit(self.game_over_surface, (0, 0))
        anti_alias = False
        result_type_surface = GameOverGui.get_font(RESULT_TYPE_FONT_SIZE).render(
            result_type.lower(), anti_alias, AssetManager.get_theme().secondary_dark)

        if game_result == MatchResult.DRAW.name:
            game_result_surface = GameOverGui.get_font(POP_UP_FONT_SIZE).render(
                DRAW_MESSAGE, anti_alias, AssetManager.get_theme().secondary_dark)
        else:
            game_result_surface = GameOverGui.get_font(POP_UP_FONT_SIZE).render(
                game_result.lower() + WINNING_MESSAGE, anti_alias, AssetManager.get_theme().secondary_dark)

        game_result_pos = game_result_surface.get_rect(midtop=self.game_result_bg.get_rect().midtop)
        result_type_pos = result_type_surface.get_rect(midbottom=self.game_result_bg.get_rect().midbottom)
        game_result_pos.y += (game_result_pos.height * 2)
        result_type_pos.y -= (result_type_pos.height * 2)
        self.game_result_bg.blit(game_result_surface, game_result_pos)
        self.game_result_bg.blit(result_type_surface, result_type_pos)
        self.quit_button.rect.midtop = self.game_result_bg.get_rect(
            center=GameSurface.get().get_rect().center).midbottom
        self.quit_button.rect.y += 20

    def is_quit_collision(self, game_offset: pygame.rect.Rect) -> bool:
        vec_offset: pygame.math.Vector2 = pygame.math.Vector2(game_offset.topleft)
        mouse_pos = pygame.math.Vector2(pygame.mouse.get_pos()) - vec_offset
        return self.quit_button.rect.collidepoint(mouse_pos.x, mouse_pos.y)

    def render(self, game_offset: pygame.rect.Rect) -> None:
        GameSurface.get().blit(self.final_frame, (0, 0))
        GameSurface.get().blit(
            self.game_result_bg,
            self.game_result_bg.get_rect(center=GameSurface.get().get_rect().center)
        )
        self.quit_button.render(game_offset)
