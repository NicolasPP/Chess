# -- Alpha --
AVAILABLE_ALPHA: int = 100
GAME_OVER_ALPHA: int = 100
HOVER_ALPHA: int = 70
VERIFY_BG_ALPHA: int = 100
OPAQUE: int = 255
PREV_MOVE_ALPHA: int = 100

# -- Size --
POP_UP_BG_WIDTH: int = 300
POP_UP_BG_HEIGHT: int = 150
POP_UP_SPACING: int = 5
POP_UP_FONT_SIZE: int = 25
RESULT_TYPE_FONT_SIZE: int = 17
AVAILABLE_MOVE_SCALE: float = 1 / 3
PROMOTION_PIECE_SCALE: float = 5/4
BOARD_SIZE: int = 8
DATA_SIZE: int = 4096
TIMER_FONT_SIZE: int = 18
DESCRIPTION_FONT_SIZE: int = 22
DESCRIPTION_BUTTON_WIDTH: int = 300
DESCRIPTION_BUTTON_HEIGHT: int = 20
VERIFY_BUTTON_WIDTH: int = 60
VERIFY_BUTTON_HEIGHT: int = 30
OFFER_DRAW_FONT_SIZE: int = 17
RESIGN_FONT_SIZE: int = 17
GUI_SPACING: int = 5
PIECE_ASSET_ROW: int = 1
PIECE_ASSET_COL: int = 6
SQUARE_SIZE: int = 16
BOARD_OUTLINE_THICKNESS: int = 4
X_AXIS_HEIGHT: int = 8
Y_AXIS_WIDTH: int = 8
OPP_TIMER_SPACING:  int = 6
AXIS_FONT_SIZE: int = 25
PLAYED_MOVE_FONT_SIZE: int = 20
DEFAULT_SCALE: float = 3.5
GAME_SURFACE_SPACING: int = 50
SCORE_FONT_SIZE: int = 25
MAX_SCORE: str = "+30"
# -- Colors --
AVAILABLE_MOVE_COLOR: tuple[int, int, int] = (76, 155, 87)
PIECE_BG: tuple[int, int, int] = (0, 0, 0)
GAME_OVER_COLOR: tuple[int, int, int] = (255, 255, 255)

THEME1_P_LIGHT: tuple[int, int, int] = (234, 240, 217)
THEME1_P_DARK: tuple[int, int, int] = (89, 96, 111)
THEME1_S_LIGHT: tuple[int, int, int] = (43, 45, 48)
THEME1_S_DARK: tuple[int, int, int] = (224, 175, 105)

THEME2_P_LIGHT: tuple[int, int, int] = (234, 240, 217)
THEME2_P_DARK: tuple[int, int, int] = (192, 196, 180)
THEME2_S_LIGHT: tuple[int, int, int] = (43, 45, 48)
THEME2_S_DARK: tuple[int, int, int] = (224, 175, 105)

THEME3_P_LIGHT: tuple[int, int, int] = (150, 162, 178)
THEME3_P_DARK: tuple[int, int, int] = (89, 96, 111)
THEME3_S_LIGHT: tuple[int, int, int] = (43, 45, 48)
THEME3_S_DARK: tuple[int, int, int] = (224, 175, 105)

THEME4_P_LIGHT: tuple[int, int, int] = (230, 234, 216)
THEME4_P_DARK: tuple[int, int, int] = (69, 77, 94)
THEME4_S_LIGHT: tuple[int, int, int] = (43, 45, 48)
THEME4_S_DARK: tuple[int, int, int] = (224, 175, 105)

# -- Default values --
SCROLL_SPEED: int = 10
GAME_START_FEN: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
OFFER_DRAW_LABEL: str = "draw"
RESIGN_LABEL: str = "resign"
YES_LABEL: str = "yes"
NO_LABEL: str = "no"
DESCRIPTION_LABEL: str = "are you sure you want to"
DRAW_DOUBLE_CHECK_LABEL: str = "offer a draw"
RESIGN_DOUBLE_CHECK_LABEL: str = "resign the game"
RESPOND_DRAW_LABEL: str = "opponent has offered a draw"
WINNING_MESSAGE: str = " is the winner!"
DRAW_MESSAGE: str = "Game Tied"

# -- File Name --
FONT_FILE: str = "assets/fonts/Oleaguid.ttf"
FIVE_FONT_FILE: str = "assets/fonts/QuinqueFive.ttf"

SIMPLE16x16_PIECE_FILE_WHITE: str = 'assets/pieces-16-16/WhitePieces_Simplified.png'
SIMPLE16x16_PIECE_FILE_BLACK: str = 'assets/pieces-16-16/BlackPieces_Simplified.png'

NORMAL16x16_PIECE_FILE_WHITE: str = 'assets/pieces-16-16/WhitePieces.png'
NORMAL16x16_PIECE_FILE_BLACK: str = 'assets/pieces-16-16/BlackPieces.png'

NORMAL16x32_PIECE_FILE_WHITE: str = 'assets/pieces-16-32/WhitePieces-Sheet.png'
NORMAL16x32_PIECE_FILE_BLACK: str = 'assets/pieces-16-32/BlackPieces-Sheet.png'

# -- Indexes --
P_ASSET_INDEX: int = 0
N_ASSET_INDEX: int = 1
R_ASSET_INDEX: int = 2
B_ASSET_INDEX: int = 3
Q_ASSET_INDEX: int = 4
K_ASSET_INDEX: int = 5

P_SCORE: int = 1
N_SCORE: int = 3
R_SCORE: int = 5
B_SCORE: int = 3
Q_SCORE: int = 9

# -- Limits --
HALF_MOVE_LIMIT = 100

# -- Mouse Click values --
MOUSECLICK_LEFT: int = 1
MOUSECLICK_MIDDLE: int = 2
MOUSECLICK_RIGHT: int = 3
MOUSECLICK_SCROLL_UP: int = 4
MOUSECLICK_SCROLL_DOWN: int = 5

# -- Logging --
SERVER_NAME: str = "server"
SERVER_LOG_FILE: str = "../Chess/log/server.log"
CLIENT_NAME: str = "client"
CLIENT_LOG_FILE: str = "../Chess/log/client.log"
LOG_FILE_MODE: str = "w"
LOG_FORMAT: str = "%(asctime)s\t%(levelname)s\t%(message)s"

# -- tkinter launcher --
WINDOW_WIDTH: int = 200
WINDOW_HEIGHT: int = 300
