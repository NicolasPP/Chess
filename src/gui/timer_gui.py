import typing

import pygame

from chess.asset.asset_manager import AssetManager
from chess.chess_timer import ChessTimer
from chess.piece_movement import Side
from chess.notation.forsyth_edwards_notation import FenChars
from chess.game_surface import GameSurface
from config import *


class TimerRects(typing.NamedTuple):
    timer: pygame.rect.Rect
    spacing: pygame.rect.Rect


class TimerGui:
    pygame.font.init()
    font = pygame.font.Font(FIVE_FONT_FILE, int((TIMER_FONT_SIZE * SCALE) / DEFAULT_FONT_SCALE))

    @staticmethod
    def calculate_timer_rects(scale: float) -> TimerRects:
        info = ChessTimer.format_seconds(0, True)
        default_pos: tuple[int, int] = 0, 0
        timer = pygame.rect.Rect(default_pos, TimerGui.font.size(info))
        spacing = pygame.rect.Rect(default_pos, (OPP_TIMER_SPACING * scale, OPP_TIMER_SPACING * scale))
        return TimerRects(timer, spacing)

    def __init__(self, match_time: float, board_rect: pygame.rect.Rect) -> None:
        self.own_timer: ChessTimer = ChessTimer(match_time)
        self.opponents_timer: ChessTimer = ChessTimer(match_time)
        self.board_rect: pygame.rect.Rect = board_rect
        self.pos_offset: pygame.math.Vector2 = pygame.math.Vector2(0, (X_AXIS_HEIGHT * SCALE))
        self.own_pos, self.opponents_pos = self.calculate_timers_pos()

    def calculate_timers_pos(self) -> tuple[pygame.math.Vector2, pygame.math.Vector2]:
        text_width, text_height = TimerGui.font.size(ChessTimer.format_seconds(650, True))

        own_rect = pygame.rect.Rect(0, 0, text_width, text_height)
        opp_rect = pygame.rect.Rect(0, 0, text_width, text_height)

        own_rect.topright = self.board_rect.bottomright
        opp_rect.bottomright = self.board_rect.topright

        return pygame.math.Vector2(own_rect.topleft) + self.pos_offset, \
               pygame.math.Vector2(opp_rect.topleft) - pygame.math.Vector2(0, OPP_TIMER_SPACING * SCALE)

    def set_offset(self, off_set: pygame.rect.Rect) -> None:
        self.pos_offset = off_set

    def recalculate_pos(self) -> None:  # not used
        self.own_pos, self.opponents_pos = self.calculate_timers_pos()

    def render(self) -> None:
        def render_timer(time_left: float, pos: pygame.math.Vector2, offset_height: bool = False) -> None:
            info = ChessTimer.format_seconds(time_left, True)
            info_render = TimerGui.font.render(info, True, AssetManager.get_theme().light_color)
            render_pos = pos
            render_rect = info_render.get_rect(topleft=(render_pos.x, render_pos.y))

            # this will only work for FIVE_FONT_FILE - "assets/fonts/QuinqueFive.ttf"
            if offset_height:
                render_pos = pos + pygame.math.Vector2(0, (render_rect.height // 6) * -1)
                render_rect = info_render.get_rect(topleft=(render_pos.x, render_pos.y))

            info_bg_surface = pygame.surface.Surface(render_rect.size)
            info_bg_surface.fill(AssetManager.get_theme().dark_color)
            GameSurface.get().blit(info_bg_surface, render_rect)
            GameSurface.get().blit(info_render, render_rect)

        render_timer(self.own_timer.time_left, self.own_pos)
        render_timer(self.opponents_timer.time_left, self.opponents_pos, True)

    def tick(self, delta_time: float) -> None:
        self.own_timer.tick(delta_time)
        self.opponents_timer.tick(delta_time)

    def update(self, side: Side, active_color: str, white_time_left: float, black_time_left: float) -> None:
        current_active_color = FenChars.WHITE_ACTIVE_COLOR.value \
            if side == Side.WHITE else FenChars.BLACK_ACTIVE_COLOR.value

        if active_color == current_active_color:
            self.own_timer.start()
            self.opponents_timer.stop()
        else:
            self.own_timer.stop()
            self.opponents_timer.start()

        if side == Side.WHITE:
            self.own_timer.set_time_left(white_time_left)
            self.opponents_timer.set_time_left(black_time_left)
        else:
            self.own_timer.set_time_left(black_time_left)
            self.opponents_timer.set_time_left(white_time_left)
