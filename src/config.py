# -- Alpha --
AVAILABLE_ALPHA: int = 100
GAME_OVER_ALPHA: int = 100
HOVER_ALPHA: int = 70
VERIFY_BG_ALPHA: int = 100
OPAQUE: int = 255

# -- Size --
VERIFY_BG_WIDTH: int = 300
VERIFY_BG_HEIGHT: int = 150
VERIFY_SPACING: int = 5
VERIFY_FONT_SIZE: int = 25
AVAILABLE_MOVE_SCALE: float = 1 / 3
BOARD_SIZE: int = 8
DATA_SIZE: int = 4096
TIMER_FONT_SIZE: int = 18
DESCRIPTION_FONT_SIZE: int = 22
DESCRIPTION_BUTTON_WIDTH: int = 300
DESCRIPTION_BUTTON_HEIGHT: int = 20
DRAW_BUTTON_WIDTH: int = 60
DRAW_BUTTON_HEIGHT: int = 30
RESIGN_BUTTON_WIDTH: int = 60
RESIGN_BUTTON_HEIGHT: int = 30
OFFER_DRAW_FONT_SIZE: int = 17
RESIGN_FONT_SIZE: int = 17
END_GAME_GUI_SPACING: int = 5
PIECE_ASSET_ROW: int = 1
PIECE_ASSET_COL: int = 6
SQUARE_SIZE: int = 16
BOARD_OUTLINE_THICKNESS: int = 4
X_AXIS_HEIGHT: int = 8
Y_AXIS_WIDTH: int = 8
OPP_TIMER_SPACING:  int = 6
AXIS_FONT_SIZE: int = 25
DEFAULT_SCALE: float = 3.5
GAME_SURFACE_SPACING: int = 50

# -- Colors --
AVAILABLE_MOVE_COLOR: tuple[int, int, int] = (76, 155, 87)
PIECE_BG: tuple[int, int, int] = (0, 0, 0)
GAME_OVER_COLOR: tuple[int, int, int] = (255, 255, 255)
VERIFY_BG_COLOR: tuple[int, int, int] = (43, 45, 48)
VERIFY_FONT_COLOR: tuple[int, int, int] = (224, 175, 105)

PLAIN1_LIGHT: tuple[int, int, int] = (234, 240, 217)
PLAIN1_DARK: tuple[int, int, int] = (89, 96, 111)

PLAIN2_LIGHT: tuple[int, int, int] = (234, 240, 217)
PLAIN2_DARK: tuple[int, int, int] = (192, 196, 180)

PLAIN3_LIGHT: tuple[int, int, int] = (150, 162, 178)
PLAIN3_DARK: tuple[int, int, int] = (89, 96, 111)

PLAIN4_LIGHT: tuple[int, int, int] = (230, 234, 216)
PLAIN4_DARK: tuple[int, int, int] = (69, 77, 94)

# -- Default values --
GAME_START_FEN: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
OFFER_DRAW_LABEL: str = "draw"
RESIGN_LABEL: str = "resign"
YES_LABEL: str = "yes"
NO_LABEL: str = "no"
DESCRIPTION_LABEL: str = "are you sure you want to"
DRAW_DOUBLE_CHECK_LABEL: str = "offer a draw"
RESIGN_DOUBLE_CHECK_LABEL: str = "resign the game"
RESPOND_DRAW_LABEL: str = "opponent has offered a draw"

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
