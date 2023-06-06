import typing

import pygame

from chess.board.side import Side
from chess.game.game_size import GameSize
from chess.notation.forsyth_edwards_notation import FenChars
from chess.timer.chess_timer import ChessTimer
from config.pg_config import FIVE_FONT_FILE
from config.pg_config import OPP_TIMER_SPACING
from config.pg_config import TIMER_FONT_SIZE
from config.pg_config import X_AXIS_HEIGHT


class TimerRects(typing.NamedTuple):
    timer: pygame.rect.Rect
    spacing: pygame.rect.Rect


class TimerGui:

    @staticmethod
    def calculate_timer_rects() -> TimerRects:
        info = ChessTimer.format_seconds(0, True)
        default_pos: tuple[int, int] = 0, 0
        timer = pygame.rect.Rect(default_pos, TimerGui.get_font().size(info))
        spacing = pygame.rect.Rect(
            default_pos,
            (OPP_TIMER_SPACING * GameSize.get_scale(), OPP_TIMER_SPACING * GameSize.get_scale())
        )
        return TimerRects(timer, spacing)

    @staticmethod
    def get_font() -> pygame.font.Font:
        return pygame.font.Font(FIVE_FONT_FILE, int(GameSize.get_relative_size(TIMER_FONT_SIZE)))

    def __init__(self, match_time: float, board_rect: pygame.rect.Rect) -> None:
        self.own_timer: ChessTimer = ChessTimer(match_time)
        self.opponents_timer: ChessTimer = ChessTimer(match_time)
        self.board_rect: pygame.rect.Rect = board_rect
        self.pos_offset: pygame.math.Vector2 = pygame.math.Vector2(0, (X_AXIS_HEIGHT * GameSize.get_scale()))
        self.own_pos, self.opponents_pos = self.calculate_timers_pos(GameSize.get_scale())

    def calculate_timers_pos(self, scale: float) -> tuple[pygame.math.Vector2, pygame.math.Vector2]:
        text_width, text_height = TimerGui.get_font().size(ChessTimer.format_seconds(650, True))

        own_rect = pygame.rect.Rect(0, 0, text_width, text_height)
        opp_rect = pygame.rect.Rect(0, 0, text_width, text_height)

        own_rect.topright = self.board_rect.bottomright
        opp_rect.bottomright = self.board_rect.topright

        return pygame.math.Vector2(own_rect.topleft) + self.pos_offset, \
            pygame.math.Vector2(opp_rect.topleft) - pygame.math.Vector2(0, OPP_TIMER_SPACING * scale)

    def render(self) -> None:
        self.own_timer.render(self.own_pos, TimerGui.get_font())
        self.opponents_timer.render(self.opponents_pos, TimerGui.get_font(), True)

    def tick(self, delta_time: float) -> None:
        self.own_timer.tick(delta_time)
        self.opponents_timer.tick(delta_time)

    def update(self, side: Side, active_color: str, white_time_left: float, black_time_left: float) -> None:
        current_active_color = FenChars.WHITE_ACTIVE_COLOR \
            if side == Side.WHITE else FenChars.BLACK_ACTIVE_COLOR

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
