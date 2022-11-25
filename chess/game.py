import typing

from chess import chess_data as CHESS

from config import *




# -- Defining Movement --
'''
this decorator creates a variable " self.available_moves() "
and "FEN_val"
inside the Piece_Info(Enum) object passed.
The function will return all possible moves for that Piece 
'''
def set_info_for(piece : CHESS.PIECES, FEN_val : str):
	def set_valid_move(get_moves : typing.Callable):
		piece.set_moves(get_moves)
		piece.set_fen( FEN_val )
		return get_moves
	return set_valid_move

@set_info_for(CHESS.PIECES.PAWN, 'P') 
def PAWN_available_moves(from_index : int, exp_fen : list[str], is_white_turn : bool) -> list[str]:
	moves = []
	up = get_fen_offset_index( is_white_turn, from_index, 1, 0 )	#up
	up_right = get_fen_offset_index( is_white_turn, from_index, 1, 1 )	#up right
	up_left = get_fen_offset_index( is_white_turn, from_index, 1, -1 )	#up left

	if up is not None and exp_fen[up] == FEN.BLANK_PIECE: moves.append(up)
	for move in [up_right, up_left]:
		if move is None: continue
		elif is_white_turn:
			if exp_fen[move].islower(): moves.append(move)
		else:
		 	if exp_fen[move].isupper(): moves.append(move) 	

	return moves

@set_info_for(CHESS.PIECES.KNIGHT, 'N') 
def KNIGHT_available_moves(from_index : int, exp_fen : list[str], is_white_turn : bool) -> list[str]:
	moves = []
	moves_offset = [
		(2,  -1),		#up_right 	
		(2,   1),		#up_left 	
		(1,  -2),		#right_up 	
		(-1, -2),		#right_down 	
		(-2, -1),		#down_right	
		(-2,  1),		#down_left 	
		(-1,  2),		#left_down
		(1,   2)		#left_up 	
	]	 	

	moves += move_fixed_amount( moves_offset, from_index, exp_fen, is_white_turn ) 	

	return moves

@set_info_for(CHESS.PIECES.ROOK, 'R') 
def ROOK_available_moves(from_index : int, exp_fen : list[str], is_white_turn : bool) -> list[str]:
	moves = []
	# f - fowards b - backwards
	up, down, right, left = get_flat_offsets()

	moves += move_until_friendly(left, from_index, exp_fen, is_white_turn)
	moves += move_until_friendly(right, from_index, exp_fen, is_white_turn)
	moves += move_until_friendly(up, from_index, exp_fen, is_white_turn)
	moves += move_until_friendly(down, from_index, exp_fen, is_white_turn)

	return moves

@set_info_for(CHESS.PIECES.BISHOP, 'B') 
def BISHOP_available_moves(from_index : int, exp_fen : list[str], is_white_turn : bool) -> list[str]:
	moves = []

	up_right, down_right, up_left, down_left = get_diagonal_offsets()

	moves += move_until_friendly(up_right, from_index, exp_fen, is_white_turn)
	moves += move_until_friendly(down_right, from_index, exp_fen, is_white_turn)
	moves += move_until_friendly(up_left, from_index, exp_fen, is_white_turn)
	moves += move_until_friendly(down_left, from_index, exp_fen, is_white_turn)

	return moves
@set_info_for(CHESS.PIECES.QUEEN, 'Q') 
def QUENN_available_moves(from_index : int, exp_fen : list[str], is_white_turn : bool) -> list[str]:
	moves = []
	moves += BISHOP_available_moves(from_index, exp_fen, is_white_turn)
	moves += ROOK_available_moves(from_index, exp_fen, is_white_turn)
	return moves


@set_info_for(CHESS.PIECES.KING, 'K') 
def KING_available_moves(from_index : int, exp_fen : list[str], is_white_turn : bool) -> list[str]:
	moves = []
	moves_offset = [
		(1,  -1),		#up_right 	
		(1,   1),		#up_left 	
		(-1, -1),		#down_right	
		(-1,  1),		#down_left 	
		(1,   0),		#up 	
		(0,  -1),		#right 	
		(-1,  0),		#down 	
		(0,   1),		#left 	
	]

	moves += move_fixed_amount( moves_offset, from_index, exp_fen, is_white_turn ) 	

	return moves
# -----------------------




# -- Piece Move Helpers --
def get_fen_offset_index( is_white_turn : bool, from_index : int, row_offset : int, col_offset : int ) -> int | None:
	row, col = get_fen_row_col( from_index )
	if is_white_turn:
		row_offset = row_offset * -1
		col_offset = col_offset * -1
	new_row = row + row_offset
	new_col = col + col_offset
	if new_row < 0 or \
		new_row > BOARD_SIZE -1: return None
	if new_col < 0 or \
		new_col > BOARD_SIZE -1: return None
	index = get_fen_index( new_row, new_col )
	return index

def get_fen_row_col( index: int ) -> tuple[int,int]:
	row = index // BOARD_SIZE
	col = index - (row * BOARD_SIZE)
	return row, col

def get_fen_index( row : int , col : int ) -> int:
	return (row * BOARD_SIZE) + col

def get_diagonal_offsets(
	) -> tuple[list[tuple[int,int]], list[tuple[int,int]], list[tuple[int,int]], list[tuple[int,int]]]:
	up_right = [(index, -index) for index in range(BOARD_SIZE)]
	down_right = [(-index, -index) for index in range(BOARD_SIZE)]
	up_left = [(index, index) for index in range(BOARD_SIZE)]
	down_left = [(-index, index) for index in range(BOARD_SIZE)]
	return up_right, down_right, up_left, down_left

def get_flat_offsets(
	)-> tuple[list[tuple[int,int]], list[tuple[int,int]], list[tuple[int,int]], list[tuple[int,int]]]:
	left = [ (0, index) for index in range(BOARD_SIZE) ]
	right = [ (0, -index) for index in range(BOARD_SIZE) ]
	up = [ (index, 0) for index in range(BOARD_SIZE) ]
	down = [ (-index, 0) for index in range(BOARD_SIZE) ]
	return up, down, right, left

def move_until_friendly( moves_offset : list[tuple[int,int]], from_index :int, exp_fen : list[str] , is_white_turn : bool ) -> list[int]:
	moves = []
	for offset in moves_offset:
		move = get_fen_offset_index( is_white_turn, from_index, *offset)
		if move is None: continue
		if move == from_index: continue
		if exp_fen[move] == FEN.BLANK_PIECE: moves.append(move)
		elif is_white_turn:
			if exp_fen[move].islower(): moves.append(move)
			break
		else: 
			if exp_fen[move].isupper(): moves.append(move)
			break
	return moves

def move_fixed_amount( moves_offset : list[tuple[int,int]], from_index :int, exp_fen : list[str] , is_white_turn : bool ) -> list[int]:
	moves = []
	for offset in moves_offset:
		move = get_fen_offset_index( is_white_turn, from_index, *offset)
		if move is None: continue
		if exp_fen[move] == FEN.BLANK_PIECE: moves.append(move)
		elif is_white_turn:
			if exp_fen[move].islower(): moves.append(move)
		else:
		 	if exp_fen[move].isupper(): moves.append(move)	
	return moves
# ------------------------



# -- Checking if Move is Valid --
def is_move_valid(from_index : int, dest_index: int, exp_fen : list[str], is_white_turn : bool) -> bool:
	if not is_from_valid(exp_fen[from_index], is_white_turn): return False
	if not is_side_valid(from_index, dest_index, exp_fen): return False
	if not is_dest_valid(from_index, dest_index, exp_fen, is_white_turn): return False
	return True

	# -- helpers --
def is_from_valid(from_piece : str, is_white_turn : bool) -> bool:
	if is_from_blank( from_piece ): return False
	if not is_from_correct_side( from_piece, is_white_turn ): return False
	return True 
def is_side_valid(from_index : int, dest_index : int, exp_fen : list[str]) -> bool:
	if is_same( from_index, dest_index): return False
	if is_same_team( exp_fen[from_index], exp_fen[dest_index]): return False
	return True 
def is_dest_valid(from_index : int, dest_index : int, exp_fen : list[str], is_white_turn : bool) -> bool:
	piece = CHESS.get_name_from_fen(exp_fen[from_index])
	available_moves = CHESS.PIECES[piece].available_moves(from_index, exp_fen, is_white_turn)
	if dest_index not in available_moves: return False
	return True 


def is_from_correct_side( from_piece, is_white : bool) -> bool:
	if is_white: return from_piece.isupper()
	return from_piece.islower() 
def is_same(from_index : int, dest_index: int) -> bool:
	return from_index == dest_index
def is_from_blank( from_piece : str) -> bool: return from_piece == FEN.BLANK_PIECE
def is_same_team( from_piece : str, dest_piece: str) -> bool:
	if dest_piece == FEN.BLANK_PIECE: return False
	return from_piece.islower() == dest_piece.islower()
# -------------------------------



