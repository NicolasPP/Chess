GRID_OFFSET : int = 7
BOARD_SIZE : int = 8
NO_SURFACE : None = None
PIECE_BG : tuple[int, int, int] = 0,0,0
C_SPLIT = '-'
EMPTY_Q : None  = None




class FEN:
	BLANK_PIECE : str = "@"
	SPLIT 		: str = '/'
	BLANK 		: str = ''
	GAME_START_FEN : str = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'




class PLAYER_COMMANDS:
	UPDATE_POS 	: str = 'update_pos'
	NEXT_TURN 	: str = 'next_turn'
