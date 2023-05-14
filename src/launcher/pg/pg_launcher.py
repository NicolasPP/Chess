import typing
import dataclasses
import enum

from launcher.pg.offline_launcher import OfflineLauncher
from launcher.pg.online_launcher import OnlineLauncher
from chess.asset.chess_assets import PieceSetAssets, Themes, ChessTheme, PieceSetAsset
from chess.timer.timer_config import TimerConfig, DefaultConfigs
from server import Server
from chess.board.side import Side

PossibleConfigValues: typing.TypeAlias = str | float | ChessTheme | PieceSetAsset | TimerConfig  | Side


class SinglePlayerGameType(enum.Enum):
    HUMAN_VS_HUMAN = enum.auto()
    HUMAN_VS_BOT = enum.auto()
    BOT_VS_BOT = enum.auto()


@dataclasses.dataclass
class PygameLauncherConfig:
    theme: ChessTheme = Themes.PLAIN1
    scale: float = 5
    piece_set: PieceSetAsset = PieceSetAssets.SIMPLE16x16
    timer_config: TimerConfig = DefaultConfigs.BULLET_1_0
    server_ip: str = '127.0.0.1'
    bot_side: Side = Side.WHITE

    def single_player_args(self) -> tuple[ChessTheme, float, PieceSetAsset, TimerConfig]:
        return self.theme, self.scale, self.piece_set, self.timer_config

    def multi_player_args(self) -> tuple[str, ChessTheme, float, PieceSetAsset]:
        return self.server_ip, self.theme, self.scale, self.piece_set

    def single_player_bot_args(self) -> tuple[ChessTheme, float, PieceSetAsset, TimerConfig, Side]:
        return self.theme, self.scale, self.piece_set, self.timer_config, self.bot_side


class PygameChessLauncher:

    def __init__(self):
        self.config: PygameLauncherConfig = PygameLauncherConfig()
        self.multi_player: OnlineLauncher = OnlineLauncher()
        self.single_player: OfflineLauncher = OfflineLauncher()
        self.server: Server = Server(self.config.timer_config)
        self.is_running: bool = False

    def get_is_running(self) -> bool:
        return self.is_running

    def launch_single_player(self, game_type: SinglePlayerGameType) -> None:
        if self.get_is_running(): return
        self.is_running = True
        if game_type is SinglePlayerGameType.HUMAN_VS_HUMAN:
            self.single_player.launch_against_human(*self.config.single_player_args())
        elif game_type is SinglePlayerGameType.BOT_VS_BOT:
            self.single_player.launch_bot_vs_bot(*self.config.single_player_bot_args())
        elif game_type is SinglePlayerGameType.HUMAN_VS_BOT:
            self.single_player.launch_against_bot(*self.config.single_player_bot_args())
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

        for name, value in new_values.items():
            wrong_type_message: str = f"got {type(value).__name__} expected: "
            if name == "theme":
                assert isinstance(value, ChessTheme), wrong_type_message + ChessTheme.__name__
                self.config.theme = value
            elif name == "scale":
                assert isinstance(value, float), wrong_type_message + float.__name__
                self.config.scale = value
            elif name == "piece_set":
                assert isinstance(value, PieceSetAsset), wrong_type_message + PieceSetAsset.__name__
                self.config.piece_set = value
            elif name == "timer_config":
                assert isinstance(value, TimerConfig), wrong_type_message + TimerConfig.__name__
                self.config.timer_config = value
            elif name == "server_ip":
                assert isinstance(value, str), wrong_type_message + str.__name__
                self.config.server_ip = value
            elif name == "bot_side":
                assert isinstance(value, Side), wrong_type_message + Side.__name__
                self.config.bot_side = value
            else:
                raise Exception(f"Launcher Config has nor variable: {name}")
