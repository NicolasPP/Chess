from __future__ import annotations
import typing
import dataclasses
import pickle

from config.tk_config import LOCAL_CONFIG_PATH

PossibleConfigValues: typing.TypeAlias = str | float | int | bool


@dataclasses.dataclass
class UserConfigData:
    theme_id: int = -1
    scale: float = 3.5
    asset_name: str = 'SMALL'
    timer_config_name: str = 'BULLET_1_0'
    server_ip: str = '127.0.0.1'
    bot_side_name: str = 'WHITE'
    bot_skill_level: int = 10
    bot_elo: int = 1350
    bot_use_time: bool = False


class UserConfig:

    config: UserConfig | None = None

    @staticmethod
    def get() -> UserConfig:
        if UserConfig.config is None:
            UserConfig.config = UserConfig()
        return UserConfig.config

    def __init__(self) -> None:
        self.data: UserConfigData = UserConfigData()
        self.load_user_config()

    def load_user_config(self) -> None:
        with open(LOCAL_CONFIG_PATH, 'rb') as file:
            pickle_user_data: bytes = file.read()
            if len(pickle_user_data) > 0:
                data = pickle.loads(pickle_user_data)
                self.data = data

    def write_config(self) -> None:
        pickle_user_data: bytes = pickle.dumps(self.data)
        with open(LOCAL_CONFIG_PATH, 'wb') as file:
            file.write(pickle_user_data)

    def update_config(self, update_local_config: bool = True, **new_values: PossibleConfigValues) -> None:

        for name, value in new_values.items():
            wrong_type_message: str = f"got {type(value).__name__} expected: "
            if name == "theme_id":
                assert isinstance(value, int), wrong_type_message + int.__name__
                self.data.theme_id = value
            elif name == "scale":
                assert isinstance(value, float), wrong_type_message + float.__name__
                self.data.scale = value
            elif name == "asset_name":
                assert isinstance(value, str), wrong_type_message + str.__name__
                self.data.asset_name = value
            elif name == "timer_config_name":
                assert isinstance(value, str), wrong_type_message + str.__name__
                self.data.timer_config_name = value
            elif name == "server_ip":
                assert isinstance(value, str), wrong_type_message + str.__name__
                self.data.server_ip = value
            elif name == "bot_side_name":
                assert isinstance(value, str), wrong_type_message + str.__name__
                self.data.bot_side_name = value
            elif name == "bot_skill_level":
                assert isinstance(value, int), wrong_type_message + int.__name__
                self.data.bot_skill_level = value
            elif name == "bot_elo":
                assert isinstance(value, int), wrong_type_message + int.__name__
                self.data.bot_elo = value
            elif name == "bot_use_time":
                assert isinstance(value, bool), wrong_type_message + bool.__name__
                self.data.bot_use_time = value
            else:
                raise Exception(f"Launcher Config has nor variable: {name}")

        if update_local_config:
            self.write_config()
