from dataclasses import dataclass
from enum import Enum
from enum import auto
from typing import TypeAlias
from logging import Logger
from logging import Formatter
from logging import FileHandler
from logging import StreamHandler
from logging import DEBUG
from logging import getLogger
from sys import stdout

from config.tk_config import BOT_LOG_FILE
from config.tk_config import BOT_NAME
from config.tk_config import CLIENT_LOG_FILE
from config.tk_config import CLIENT_NAME
from config.tk_config import DATABASE_LOG_FILE
from config.tk_config import DATABASE_NAME
from config.tk_config import LOG_FILE_MODE
from config.tk_config import LOG_FORMAT
from config.tk_config import ONLINE_LAUNCHER_LOG_FILE
from config.tk_config import ONLINE_LAUNCHER_NAME
from config.tk_config import SERVER_LOG_FILE
from config.tk_config import SERVER_NAME

formatter: Formatter = Formatter(LOG_FORMAT)


class LoggingOut(Enum):
    FILE = auto()
    STDOUT = auto()


class AppLoggers(Enum):
    SERVER = auto()
    CLIENT = auto()
    BOT = auto()
    DATABASE = auto()
    ONLINE_LAUNCHER = auto()


@dataclass
class LoggingConfig:
    name: str
    out: LoggingOut
    file: str

    def get_handler(self) -> FileHandler | StreamHandler:
        if self.out is LoggingOut.FILE:
            return FileHandler(self.file, mode=LOG_FILE_MODE)

        elif self.out is LoggingOut.STDOUT:
            return StreamHandler(stdout)

        else:
            raise Exception(f"logging out type : {self.out} is invalid")


LoggerConfigTypes: TypeAlias = LoggingOut | str


class LoggingManager:
    configs: dict[AppLoggers, LoggingConfig] = {}

    @staticmethod
    def load_configs() -> None:
        out: LoggingOut = LoggingOut.FILE
        LoggingManager.configs[AppLoggers.SERVER] = LoggingConfig(SERVER_NAME, out, SERVER_LOG_FILE)
        LoggingManager.configs[AppLoggers.CLIENT] = LoggingConfig(CLIENT_NAME, out, CLIENT_LOG_FILE)
        LoggingManager.configs[AppLoggers.BOT] = LoggingConfig(BOT_NAME, out, BOT_LOG_FILE)
        LoggingManager.configs[AppLoggers.DATABASE] = LoggingConfig(DATABASE_NAME, out, DATABASE_LOG_FILE)
        LoggingManager.configs[AppLoggers.ONLINE_LAUNCHER] = LoggingConfig(ONLINE_LAUNCHER_NAME, out,
                                                                           ONLINE_LAUNCHER_LOG_FILE)

    @staticmethod
    def configure(logger: AppLoggers, **attrs: LoggerConfigTypes) -> None:
        config: LoggingConfig = LoggingManager.get_config(logger)

        for name, value in attrs.items():

            if name == "out":
                assert isinstance(value, LoggingOut), "value must be instance of AppLoggers"
                config.out = value
            elif name == "name":
                assert isinstance(value, str), "value must be instance of str"
                config.name = value
            elif name == "file":
                assert isinstance(value, str), "value must be instance of str"
                config.file = value
            else:
                raise Exception(f"{name} is not a part of logging config")

    @staticmethod
    def get_config(app_logger: AppLoggers) -> LoggingConfig:
        config: LoggingConfig | None = LoggingManager.configs.get(app_logger)
        assert config is not None, f"logger's {app_logger.name} has not been loaded"
        return config

    @staticmethod
    def get_logger(app_logger: AppLoggers) -> Logger:
        config: LoggingConfig = LoggingManager.get_config(app_logger)
        handler: FileHandler | StreamHandler = config.get_handler()
        handler.setFormatter(formatter)
        logger: Logger = getLogger(f"{config.name}:logger")
        logger.setLevel(DEBUG)
        logger.addHandler(handler)
        return logger
