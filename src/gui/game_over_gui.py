import pygame

from chess.game.game_surface import GameSurface
from chess.game.game_size import GameSize
from chess.game.chess_match import MatchResult
from config import *


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
        self.game_over_surface.set_alpha(GAME_OVER_ALPHA)
        self.game_result_bg.fill(POP_UP_BG_COLOR)
        self.bg_color: tuple[int, int, int] = bg_color

    def set_final_frame(self, game_result: str, result_type: str) -> None:
        self.final_frame.blit(GameSurface.get(), (0, 0))
        self.game_over_surface.fill(GAME_OVER_COLOR)
        self.final_frame.blit(self.game_over_surface, (0, 0))
        anti_alias = False
        result_type_surface = GameOverGui.get_font(RESULT_TYPE_FONT_SIZE).render(
            result_type.lower(), anti_alias, POP_UP_FONT_COLOR)

        if game_result == MatchResult.DRAW.name:
            game_result_surface = GameOverGui.get_font(POP_UP_FONT_SIZE).render(
                DRAW_MESSAGE, anti_alias, POP_UP_FONT_COLOR)
        else:
            game_result_surface = GameOverGui.get_font(POP_UP_FONT_SIZE).render(
                game_result.lower() + WINNING_MESSAGE, anti_alias, POP_UP_FONT_COLOR)

        game_result_pos = game_result_surface.get_rect(midtop=self.game_result_bg.get_rect().midtop)
        result_type_pos = result_type_surface.get_rect(midbottom=self.game_result_bg.get_rect().midbottom)
        game_result_pos.y += (game_result_pos.height * 2)
        result_type_pos.y -= (result_type_pos.height * 2)
        self.game_result_bg.blit(game_result_surface, game_result_pos)
        self.game_result_bg.blit(result_type_surface, result_type_pos)

    def render(self) -> None:
        GameSurface.get().fill(self.bg_color)
        GameSurface.get().blit(self.final_frame, (0, 0))
        GameSurface.get().blit(
            self.game_result_bg,
            self.game_result_bg.get_rect(center=GameSurface.get().get_rect().center)
        )
