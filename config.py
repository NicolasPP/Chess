GRID_OFFSET : int = 7
BOARD_SIZE : int = 8
NO_SURFACE : None = None
PIECE_BG : tuple[int, int, int] = 0,0,0
EMPTY_Q : None  = None
AVAILABLE_MOVE_COLOR : str = 'green'
AVAILABLE_ALPHA : int = 70
BOARD_SCALE : float = 3.5
WINDOW_SIZE : tuple[int,int] = 570, 570



class FEN:
	BLANK_PIECE : str = "@"
	SPLIT 		: str = '/'
	BLANK 		: str = ''
	GAME_START_FEN : str = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'




class PLAYER_COMMANDS:
	UPDATE_POS 		: str = 'update_pos'
	NEXT_TURN 		: str = 'next_turn'
	INVALID_MOVE 	: str = 'invalid_move'

END_MARKER : str = '#'
NO_INFO : str = '<>'
I_SPLIT : str = '-'
C_SPLIT : str = '%'
DATA_SIZE : int = 4096
