# -- Alpha --
AVAILABLE_ALPHA : int = 70

# -- Size --
WINDOW_SIZE : tuple[int,int] = 570, 570
BOARD_SCALE : float = 3.5
BOARD_SIZE : int = 8
DATA_SIZE : int = 4096

# -- Colors --
AVAILABLE_MOVE_COLOR : str = 'green'
PIECE_BG : tuple[int, int, int] = 0,0,0

# -- Default vals --
GAME_START_FEN : str = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'
CHECK_MATE_CHECK : str = 'rnbqkbnr/pppp1ppp/8/4p3/8/5PP1/PPPPP11P/RNBQKBNR'
GRID_OFFSET : int = 7
NO_SURFACE : None = None
EMPTY_Q : None  = None

# -- Data operations --
END_MARKER : str = '#'
NO_INFO : str = '<>'
I_SPLIT : str = '-'
C_SPLIT : str = '%'
