import pygame

from chess.chess_timer import ChessTimer
from chess.board import SIDE
from utils.forsyth_edwards_notation import FenChars
from config import FIVE_FONT_FILE, TIMER_FONT_SIZE


class TimerGui:
    pygame.font.init()
    font = pygame.font.Font(FIVE_FONT_FILE, TIMER_FONT_SIZE)

    @staticmethod
    def calculate_timers_pos(board_rect: pygame.rect.Rect) -> tuple[pygame.math.Vector2, pygame.math.Vector2]:
        text_width, text_height = TimerGui.font.size(ChessTimer.format_seconds(650, True))

        own_rect = pygame.rect.Rect(0, 0, text_width, text_height)
        opp_rect = pygame.rect.Rect(0, 0, text_width, text_height)

        own_rect.topright = board_rect.bottomright
        opp_rect.bottomright = board_rect.topright

        return pygame.math.Vector2(own_rect.topleft), pygame.math.Vector2(opp_rect.topleft)

    def __init__(self, match_time: float, board_rect: pygame.rect.Rect) -> None:
        self.own_timer = ChessTimer(match_time)
        self.opponents_timer = ChessTimer(match_time)
        self.board_rect = board_rect
        self.own_pos, self.opponents_pos = TimerGui.calculate_timers_pos(board_rect)

    def recalculate_pos(self):
        self.own_pos, self.opponents_pos = TimerGui.calculate_timers_pos(self.board_rect)

    def render(self) -> None:
        bg_color = 'white'
        fg_color = 'black'

        own_info = ChessTimer.format_seconds(self.own_timer.time_left, True)
        opp_info = ChessTimer.format_seconds(self.opponents_timer.time_left, True)

        own_render = TimerGui.font.render(own_info, True, fg_color)
        opp_render = TimerGui.font.render(opp_info, True, fg_color)

        own_rect = own_render.get_rect(topleft=(self.own_pos.x, self.own_pos.y))
        opp_rect = opp_render.get_rect(topleft=(self.opponents_pos.x, self.opponents_pos.y))

        own_bg_surface = pygame.surface.Surface(own_rect.size)
        own_bg_surface.fill(bg_color)
        opp_bg_surface = pygame.surface.Surface(opp_rect.size)
        opp_bg_surface.fill(bg_color)

        pygame.display.get_surface().blit(own_bg_surface, own_rect)
        pygame.display.get_surface().blit(own_render, own_rect)

        pygame.display.get_surface().blit(opp_bg_surface, opp_rect)
        pygame.display.get_surface().blit(opp_render, opp_rect)

    def tick(self, delta_time: float) -> None:
        self.own_timer.tick(delta_time)
        self.opponents_timer.tick(delta_time)

    def update(self, side: SIDE, active_color: str, white_time_left: float, black_time_left: float) -> None:
        current_active_color = FenChars.WHITE_ACTIVE_COLOR.value \
            if side == SIDE.WHITE else FenChars.BLACK_ACTIVE_COLOR.value

        if active_color == current_active_color:
            self.own_timer.start()
            self.opponents_timer.stop()
        else:
            self.own_timer.stop()
            self.opponents_timer.start()

        if side == SIDE.WHITE:
            self.own_timer.set_time_left(white_time_left)
            self.opponents_timer.set_time_left(black_time_left)
        else:
            self.own_timer.set_time_left(black_time_left)
            self.opponents_timer.set_time_left(white_time_left)
