# -- Alpha --
AVAILABLE_ALPHA: int = 100
GAME_OVER_ALPHA: int = 100


# -- Size --
WINDOW_SIZE: tuple[int, int] = 570, 570
BOARD_SCALE: float = 3.5
AVAILABLE_MOVE_SCALE: float = 1/3
BOARD_SIZE: int = 8
DATA_SIZE: int = 4096
TIMER_FONT_SIZE: int = 15
DRAW_BUTTON_WIDTH: int = 60
DRAW_BUTTON_HEIGHT: int = 30
RESIGN_BUTTON_WIDTH: int = 60
RESIGN_BUTTON_HEIGHT: int = 30
OFFER_DRAW_FONT_SIZE: int = 17
RESIGN_FONT_SIZE: int = 17
END_GAME_GUI_SPACING: int = 5
PIECE_ASSET_ROW: int = 1
PIECE_ASSET_COL: int = 6

# -- Colors --
AVAILABLE_MOVE_COLOR: tuple[int, int, int] = 76, 155, 87
PIECE_BG: tuple[int, int, int] = (0, 0, 0)
GAME_OVER_COLOR: tuple[int, int, int] = (255, 255, 255)

PLAIN1_BG: tuple[int, int, int] = (234, 240, 217)
PLAIN1_FG: tuple[int, int, int] = (89, 96, 111)

PLAIN2_BG: tuple[int, int, int] = (234, 240, 217)
PLAIN2_FG: tuple[int, int, int] = (192, 196, 180)

PLAIN3_BG: tuple[int, int, int] = (150, 162, 178)
PLAIN3_FG: tuple[int, int, int] = (89, 96, 111)

PLAIN4_BG: tuple[int, int, int] = (230, 234, 216)
PLAIN4_FG: tuple[int, int, int] = (69, 77, 94)


# -- Default vals --
GAME_START_FEN: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
GRID_OFFSET: int = 7
OFFER_DRAW_LABEL: str = "draw"
RESIGN_LABEL: str = "resign"

# -- File Name --
FONT_FILE: str = "assets/fonts/Oleaguid.ttf"
FIVE_FONT_FILE: str = "assets/fonts/QuinqueFive.ttf"

# -- Indexes --
P_ASSET_INDEX = 0
N_ASSET_INDEX = 1
R_ASSET_INDEX = 2
B_ASSET_INDEX = 3
Q_ASSET_INDEX = 4
K_ASSET_INDEX = 5

# -- Limits --
HALF_MOVE_LIMIT = 100
