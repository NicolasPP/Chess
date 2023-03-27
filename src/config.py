# -- Alpha --
AVAILABLE_ALPHA: int = 70

# -- Size --
WINDOW_SIZE: tuple[int, int] = 570, 570
BOARD_SCALE: float = 3.5
BOARD_SIZE: int = 8
DATA_SIZE: int = 4096
TIMER_FONT_SIZE: int = 15

# -- Colors --
AVAILABLE_MOVE_COLOR: str = 'green'
PIECE_BG: tuple[int, int, int] = 0, 0, 0

# -- Default vals --
GAME_START_FEN: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
GRID_OFFSET: int = 7
NO_SURFACE: None = None
EMPTY_Q: None = None

# -- Data operations --
END_MARKER: str = '#'
NO_INFO: str = '<>'
I_SPLIT: str = '*'
C_SPLIT: str = '%'

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
