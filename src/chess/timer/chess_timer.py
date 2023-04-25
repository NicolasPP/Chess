import pygame

from chess.asset.asset_manager import AssetManager
from chess.game.game_surface import GameSurface


class ChessTimer:
    @staticmethod
    def format_seconds(time: float, milli_seconds: bool = False) -> str:

        def format_time(f_time: str) -> str:
            if len(f_time) == 1:
                if f_time == "0":
                    return f_time + "0"
                else:
                    return "0" + f_time
            return f_time

        div, mod = divmod(time, 60)
        seconds = str(round(mod, 1)).split('.')
        if len(seconds) == 1: seconds.append("0")
        minutes = int(div)
        secs, m_secs = seconds
        str_minutes = format_time(str(minutes))
        secs = format_time(secs)
        m_secs = format_time(m_secs)

        if secs == "0": secs += "0"
        if milli_seconds:
            return f"{str_minutes}:{secs}:{m_secs}"
        return f"{str_minutes}:{secs}"

    def __init__(self, seconds: float):
        self.time_left: float = seconds
        self.decrement_time = False

    def is_time_over(self) -> bool:
        return self.time_left <= 0

    def tick(self, dt: float) -> None:
        if not self.decrement_time: return
        if self.time_left <= 0: return
        self.time_left -= dt
        if self.time_left < 0: self.time_left = 0

    def set_time_left(self, time_left):
        self.time_left = time_left

    def start(self) -> None:
        self.decrement_time = True

    def stop(self) -> None:
        self.decrement_time = False

    def render(self, pos: pygame.math.Vector2, font: pygame.font.Font, offset_height: bool = False) -> None:
        info = ChessTimer.format_seconds(self.time_left, True)
        info_render = font.render(info, True, AssetManager.get_theme().primary_light)
        render_pos = pos
        render_rect = info_render.get_rect(topleft=(render_pos.x, render_pos.y))

        # this will only work for FIVE_FONT_FILE - "assets/fonts/QuinqueFive.ttf"
        if offset_height:
            render_pos = pos + pygame.math.Vector2(0, (render_rect.height // 6) * -1)
            render_rect = info_render.get_rect(topleft=(render_pos.x, render_pos.y))

        info_bg_surface = pygame.surface.Surface(render_rect.size)
        info_bg_surface.fill(AssetManager.get_theme().primary_dark)
        GameSurface.get().blit(info_bg_surface, render_rect)
        GameSurface.get().blit(info_render, render_rect)
