DEFAULT_WINDOW_WIDTH: int = 860
DEFAULT_WINDOW_HEIGHT: int = 300

FONT_NAME: str = "Verdana"

BG_DARK: str = '#343A40'
BG_LIGHT: str = '#3B4754'
FG_LIGHT: str = '#FFF8DC'
FG_DARK: str = '#E0AF69'

LAUNCHER_PAD: int = 10
SETTINGS_PAD: int = 15
TIME_ENTRY_PAD: int = 15
USER_CARD_SPACING: int = 20

DEFAULT_FONT_SIZE: int = 13
FRAME_FONT_SIZE: int = 15
CONNECT_ERROR_WRAP_LEN: int = 300

PATH_ENTRY_WIDTH: int = 18
DEFAULT_CARD_HEIGHT: int = 70
SCALE_LABEL_WIDTH: int = 8
TIME_ENTRY_WIDTH: int = 5
SETTINGS_MENUBUTTON_WIDTH: int = 11

SCROLLBAR_WIDTH: int = 11
CANVAS_WINDOW_POS: tuple[int, int] = 0, 0

LOCAL_CONFIG_PATH: str = 'src/config/user_config.txt'

MAX_ELO: int = 3544
MIN_ELO: int = 0
MAX_SKILL: int = 20
MIN_SKILL: int = 0
MAX_SIZE: int = 7
MIN_SIZE: int = 3

MAX_CONNECTIONS: int = 64

CHESS_DB_INFO: tuple[str, str, str, int, str] = 'root', 'chess-database', '35.197.134.140', 3306, 'chess_db'
LOCAL_CHESS_DB_INFO: tuple[str, str, str, int, str] = 'root', 'nicolas', '127.0.0.1', 3306, 'local_chess_db'

# -- Logging --
SERVER_NAME: str = "server"
CLIENT_NAME: str = "client"
DATABASE_NAME: str = "database"
BOT_NAME: str = "bot"
SERVER_LOG_FILE: str = "../Chess/log/server.log"
DATABASE_LOG_FILE: str = "../Chess/log/database.log"
BOT_LOG_FILE: str = "../Chess/log/bot.log"
CLIENT_LOG_FILE: str = "../Chess/log/client.log"
LOG_FILE_MODE: str = "w"
LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
