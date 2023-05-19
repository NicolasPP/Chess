import typing
import enum

from launcher.pg.offline_launcher import OfflineLauncher
from launcher.pg.online_launcher import OnlineLauncher
from chess.timer.timer_config import DefaultConfigs
from config.user_config import UserConfig, PossibleConfigValues
from server import Server


class SinglePlayerGameType(enum.Enum):
    HUMAN_VS_HUMAN = enum.auto()
    HUMAN_VS_BOT = enum.auto()
    BOT_VS_BOT = enum.auto()


class ChessPygameLauncher:

    def __init__(self, show_app: typing.Callable[[], None] | None = None, hide_app: typing.Callable[[], None] | None
                 = None):
        self.config: UserConfig = UserConfig()
        self.multi_player: OnlineLauncher = OnlineLauncher()
        self.single_player: OfflineLauncher = OfflineLauncher()
        self.server: Server = Server(DefaultConfigs.get_timer_config(self.config.data.timer_config_name))
        self.is_running: bool = False
        self.show_app: typing.Callable[[], None] | None = show_app
        self.hide_app: typing.Callable[[], None] | None = hide_app

    def get_is_running(self) -> bool:
        return self.is_running

    def launch_single_player(self, game_type: SinglePlayerGameType) -> None:
        if self.get_is_running(): return
        self.is_running = True
        if self.hide_app is not None:
            self.hide_app()
        if game_type is SinglePlayerGameType.HUMAN_VS_HUMAN:
            self.single_player.launch_against_human(*self.config.single_player_args())
        elif game_type is SinglePlayerGameType.BOT_VS_BOT:
            self.single_player.launch_bot_vs_bot(*self.config.single_player_bot_args())
        elif game_type is SinglePlayerGameType.HUMAN_VS_BOT:
            self.single_player.launch_against_bot(*self.config.single_player_bot_args())
        self.is_running = False
        if self.show_app is not None:
            self.show_app()

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
            if name == "theme_id":
                assert isinstance(value, int), wrong_type_message + int.__name__
                self.config.data.theme_id = value
            elif name == "scale":
                assert isinstance(value, float), wrong_type_message + float.__name__
                self.config.data.scale = value
            elif name == "asset_name":
                assert isinstance(value, str), wrong_type_message + str.__name__
                self.config.data.asset_name = value
            elif name == "timer_config_name":
                assert isinstance(value, str), wrong_type_message + str.__name__
                self.config.data.timer_config_name = value
            elif name == "server_ip":
                assert isinstance(value, str), wrong_type_message + str.__name__
                self.config.data.server_ip = value
            elif name == "bot_side_name":
                assert isinstance(value, str), wrong_type_message + str.__name__
                self.config.data.bot_side = value
            else:
                raise Exception(f"Launcher Config has nor variable: {name}")

        self.config.write_config()
