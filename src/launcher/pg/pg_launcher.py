import typing
import dataclasses
import enum

from launcher.pg.offline_launcher import OfflineLauncher
from launcher.pg.online_launcher import OnlineLauncher
from chess.asset.chess_assets import PieceSetAssets, Themes, ChessTheme, PieceSetAsset
from chess.timer.timer_config import TimerConfig
from server import Server

PossibleConfigValues: typing.TypeAlias = str | float | ChessTheme | PieceSetAsset | TimerConfig


class Opponent(enum.Enum):
    HUMAN = enum.auto()
    BOT = enum.auto()


@dataclasses.dataclass
class PygameLauncherConfig:
    theme: ChessTheme = Themes.PLAIN1
    scale: float = 3.5
    piece_set: PieceSetAsset = PieceSetAssets.SIMPLE16x16
    timer_config: TimerConfig = TimerConfig(60 * 10, 0)
    server_ip: str = '127.0.0.1'

    def single_player_args(self) -> tuple[ChessTheme, float, PieceSetAsset, TimerConfig]:
        return self.theme, self.scale, self.piece_set, self.timer_config

    def multi_player_args(self) -> tuple[str, ChessTheme, float, PieceSetAsset]:
        return self.server_ip, self.theme, self.scale, self.piece_set


class PygameChessLauncher:

    def __init__(self):
        self.config: PygameLauncherConfig = PygameLauncherConfig()
        self.multi_player: OnlineLauncher = OnlineLauncher()
        self.single_player: OfflineLauncher = OfflineLauncher()
        self.server: Server = Server(self.config.timer_config)
        self.is_running: bool = False

    def get_is_running(self) -> bool:
        return self.is_running

    def launch_single_player(self, opponent: Opponent) -> None:
        if self.get_is_running(): return
        self.is_running = True
        if opponent is Opponent.HUMAN:
            self.single_player.launch_against_human(*self.config.single_player_args())
        elif opponent is Opponent.BOT:
            self.single_player.launch_against_bot(*self.config.single_player_args())
        self.is_running = False

    def launch_multi_player_client(self) -> None:
        if self.get_is_running(): return
        self.is_running = True
        self.multi_player.launch(*self.config.multi_player_args())
        self.is_running = False

    def run_local_server(self) -> None:
        if self.get_is_running(): return
        self.is_running = True
        self.server.run()
        self.is_running = False

    def update_config(self, **new_values: PossibleConfigValues) -> None:

        def assert_type(val, val_type) -> None:
            assert isinstance(val, val_type), f"got: {type(val).__name__} expected: {val_type.__name__}"

        for name, value in new_values.items():
            if name == "theme":
                assert_type(value, ChessTheme)
                self.config.theme = value
            elif name == "scale":
                assert_type(value, float)
                self.config.scale = value
            elif name == "piece_set":
                assert_type(value, PieceSetAsset)
                self.config.piece_set = value
            elif name == "timer_config":
                assert_type(value, TimerConfig)
                self.config.timer_config = value
            elif name == "server_ip":
                assert_type(value, str)
                self.config.server_ip = value
            else:
                raise Exception(f"Launcher Config has nor variable: {name}")
