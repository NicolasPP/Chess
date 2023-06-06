import enum
import logging
import sys

from config.tk_config import LOG_FILE_MODE
from config.tk_config import LOG_FORMAT

formatter: logging.Formatter = logging.Formatter(LOG_FORMAT)


class LoggingOut(enum.Enum):
    FILE = enum.auto()
    STDOUT = enum.auto()


def set_up_logging(name: str, out_type: LoggingOut, log_file: str | None = None, log_level=logging.DEBUG) -> \
        logging.Logger:
    handler: logging.FileHandler | logging.StreamHandler = get_handler(out_type, log_file)
    handler.setFormatter(formatter)
    logger: logging.Logger = logging.getLogger(f"{name}:logger")
    logger.setLevel(log_level)
    logger.addHandler(handler)
    return logger


def get_handler(out_type: LoggingOut, log_file: str | None = None) -> logging.FileHandler | logging.StreamHandler:
    if out_type is LoggingOut.FILE:
        assert log_file is not None, "if out type is FILE must provide file path"
        return logging.FileHandler(log_file, mode=LOG_FILE_MODE)

    elif out_type is LoggingOut.STDOUT:
        return logging.StreamHandler(sys.stdout)

    else:
        raise Exception(f"logging out type : {out_type} is invalid")
