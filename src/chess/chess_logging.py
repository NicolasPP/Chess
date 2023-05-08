import logging
from config.pg_config import LOG_FORMAT, LOG_FILE_MODE
formatter: logging.Formatter = logging.Formatter(LOG_FORMAT)


def set_up_logging(name: str, log_file: str, log_level=logging.DEBUG) -> logging.Logger:
    handler: logging.FileHandler = logging.FileHandler(log_file, mode=LOG_FILE_MODE)
    handler.setFormatter(formatter)

    logger: logging.Logger = logging.getLogger(name)
    logger.setLevel(log_level)
    logger.addHandler(handler)

    return logger
