import dataclasses
from utils.forsyth_edwards_notation import Fen


@dataclasses.dataclass
class TimerConfig:
    # seconds
    time: float
    increment: float


class DefaultConfigs:
    # Bullet time controls refer to any time control that is faster than three minutes per player.
    BULLET_1 = TimerConfig(1 * 60, 0)
    BULLET_1_1 = TimerConfig(1 * 60, 1)
    BULLET_2_1 = TimerConfig(2 * 60, 1)

    # Blitz time controls are between three and ten minutes per player.
    BLITZ_3 = TimerConfig(3 * 60, 0)
    BLITZ_3_2 = TimerConfig(3 * 60, 2)
    BLITZ_5 = TimerConfig(5 * 60, 0)

    # Rapid time controls are any time controls that are longer than ten minutes per player.
    RAPID_15_10 = TimerConfig(15 * 60, 10)
    RAPID_30 = TimerConfig(30 * 60, 0)
    RAPID_60 = TimerConfig(60 * 60, 0)


class ChessTimer:
    @staticmethod
    def format_seconds(time: float) -> str:
        div, mod = divmod(time, 60)
        seconds = str(round(mod, 1)).split('.')
        if len(seconds) == 1: seconds.append("0")
        minutes = int(div)
        secs, m_secs = seconds
        return f"{minutes} : {secs} : {m_secs}"

    def __init__(self, cfg: TimerConfig):
        self.white_time_left: float = cfg.time
        self.black_time_left: float = cfg.time

    def is_time_over(self, fen: Fen) -> bool:
        if fen.is_white_turn():
            return self.white_time_left <= 0
        else:
            return self.black_time_left <= 0

    def tick(self, dt: float, fen: Fen) -> None:
        if not fen.first_move: return
        if fen.is_white_turn():
            self.decrement_white_time(dt)
        else:
            self.decrement_black_time(dt)

    def decrement_white_time(self, dt: float):
        if self.white_time_left <= 0: return
        self.white_time_left -= dt
        if self.white_time_left < 0: self.white_time_left = 0

    def decrement_black_time(self, dt: float):
        if self.black_time_left <= 0: return
        self.black_time_left -= dt
        if self.black_time_left < 0: self.black_time_left = 0
