from utils.debug import debug
from chess.chess_timer import ChessTimer
from chess.board import SIDE
from utils.forsyth_edwards_notation import FenChars


class TimerGui:
    def __init__(self, match_time: float) -> None:
        self.own_timer = ChessTimer(match_time)
        self.opponents_timer = ChessTimer(match_time)

    def render(self) -> None:
        debug(ChessTimer.format_seconds(self.own_timer.time_left))
        debug(ChessTimer.format_seconds(self.opponents_timer.time_left), x=200)

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
