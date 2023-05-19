import typing
import dataclasses
import pickle

from chess.asset.chess_assets import PieceSetAssets, Themes, ChessTheme, PieceSetAsset
from chess.timer.timer_config import TimerConfig, DefaultConfigs
from chess.board.side import Side
from config.tk_config import *

PossibleConfigValues: typing.TypeAlias = str | float | int


@dataclasses.dataclass
class UserConfigData:
    theme_id: int = -1
    scale: float = 5.0
    asset_name: str = 'SMALL'
    timer_config_name: str = 'BULLET_1_0'
    server_ip: str = '127.0.0.1'
    bot_side_name: str = 'WHITE'


class UserConfig:
    def __init__(self) -> None:
        self.data: UserConfigData = UserConfigData()
        self.load_user_config()

    def load_user_config(self) -> None:
        with open(LOCAL_CONFIG_PATH, 'rb') as file:
            pickle_user_data: bytes = file.read()
            if len(pickle_user_data) > 0:
                data = pickle.loads(pickle_user_data)
                self.data = data
            file.close()

    def write_config(self) -> None:
        pickle_user_data: bytes = pickle.dumps(self.data)
        with open(LOCAL_CONFIG_PATH, 'wb') as file:
            file.write(pickle_user_data)

    def single_player_args(self) -> tuple[ChessTheme, float, PieceSetAsset, TimerConfig]:
        theme: ChessTheme = Themes.get_theme(self.data.theme_id)
        piece_set: PieceSetAsset = PieceSetAssets.get_asset(self.data.asset_name)
        timer_config: TimerConfig = DefaultConfigs.get_timer_config(self.data.timer_config_name)
        return theme, self.data.scale, piece_set, timer_config

    def multi_player_args(self) -> tuple[str, ChessTheme, float, PieceSetAsset]:
        theme: ChessTheme = Themes.get_theme(self.data.theme_id)
        piece_set: PieceSetAsset = PieceSetAssets.get_asset(self.data.asset_name)
        return self.data.server_ip, theme, self.data.scale, piece_set

    def single_player_bot_args(self) -> tuple[ChessTheme, float, PieceSetAsset, TimerConfig, Side]:
        theme: ChessTheme = Themes.get_theme(self.data.theme_id)
        piece_set: PieceSetAsset = PieceSetAssets.get_asset(self.data.asset_name)
        bot_side: Side = Side[self.data.bot_side_name]
        timer_config: TimerConfig = DefaultConfigs.get_timer_config(self.data.timer_config_name)
        return theme, self.data.scale, piece_set, timer_config, bot_side
