import typing

from chess import chess_data as CHESS
from utils import FEN_notation as FEN

from config import *


'''
class BOARD_STATE(enum.Enum):
	CHECK
	CHECKMATE
	NORMAL


- check if move is valid:
	match get_board_state(fen):
		case BOARD_STATE.CHECK:

	- get possible moves according to how piece moves
	- filter moves that leave king vunerable
	- if the king is checked, 
'''

# -- Defining Movement --
'''
this decorator creates a variable " self.available_moves() "
and "FEN_val"
inside the Piece_Info(Enum) object passed.
The function will return all possible moves for that Piece 
'''
def set_info_for(piece : CHESS.PIECES, FEN_val : str):
	def set_valid_move(get_valid_moves : typing.Callable):
		piece.set_moves(get_valid_moves)
		piece.set_fen(FEN_val)
		return get_valid_moves
	return set_valid_move

@set_info_for(CHESS.PIECES.PAWN, 'P') 
def PAWN_available_moves(from_index : int, exp_fen : list[str], is_white_turn : bool) -> list[int]:
	moves = []
	up = get_fen_offset_index(is_white_turn, from_index, 1, 0)	#up
	up_right = get_fen_offset_index(is_white_turn, from_index, 1, 1)	#up right
	up_left = get_fen_offset_index(is_white_turn, from_index, 1, -1)	#up left

	if up is not None and exp_fen[up] == FEN.FEN_CHARS.BLANK_PIECE.value: moves.append(up)
	for move in [up_right, up_left]:
		if move is None: continue
		elif is_white_turn:
			if exp_fen[move].islower(): moves.append(move)
		else:
			if exp_fen[move].isupper(): moves.append(move) 	

	return moves

@set_info_for(CHESS.PIECES.KNIGHT, 'N') 
def KNIGHT_available_moves(from_index : int, exp_fen : list[str], is_white_turn : bool) -> list[int]:
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

	moves += move_fixed_amount(moves_offset, from_index, exp_fen, is_white_turn) 	

	return moves

@set_info_for(CHESS.PIECES.ROOK, 'R') 
def ROOK_available_moves(from_index : int, exp_fen : list[str], is_white_turn : bool) -> list[int]:
	moves = []
	# f - fowards b - backwards
	up, down, right, left = get_flat_offsets()

	moves += move_until_friendly(left, from_index, exp_fen, is_white_turn)
	moves += move_until_friendly(right, from_index, exp_fen, is_white_turn)
	moves += move_until_friendly(up, from_index, exp_fen, is_white_turn)
	moves += move_until_friendly(down, from_index, exp_fen, is_white_turn)

	return moves

@set_info_for(CHESS.PIECES.BISHOP, 'B') 
def BISHOP_available_moves(from_index : int, exp_fen : list[str], is_white_turn : bool) -> list[int]:
	moves = []

	up_right, down_right, up_left, down_left = get_diagonal_offsets()

	moves += move_until_friendly(up_right, from_index, exp_fen, is_white_turn)
	moves += move_until_friendly(down_right, from_index, exp_fen, is_white_turn)
	moves += move_until_friendly(up_left, from_index, exp_fen, is_white_turn)
	moves += move_until_friendly(down_left, from_index, exp_fen, is_white_turn)

	return moves
@set_info_for(CHESS.PIECES.QUEEN, 'Q') 
def QUENN_available_moves(from_index : int, exp_fen : list[str], is_white_turn : bool) -> list[int]:
	moves = []
	moves += BISHOP_available_moves(from_index, exp_fen, is_white_turn)
	moves += ROOK_available_moves(from_index, exp_fen, is_white_turn)
	return moves


@set_info_for(CHESS.PIECES.KING, 'K') 
def KING_available_moves(from_index : int, exp_fen : list[str], is_white_turn : bool) -> list[int]:
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

	moves += move_fixed_amount(moves_offset, from_index, exp_fen, is_white_turn) 	

	return moves
# -----------------------




# -- Piece Move Helpers --
def get_available_moves(piece_name : str, from_index : int, exp_fen : list[str], is_white_turn : bool) -> list[int]:
	available_moves = CHESS.PIECES[piece_name].available_moves(from_index, exp_fen, is_white_turn)
	safe_moves = []
	for move in available_moves:
		if is_king_safe(from_index, move, FEN.pack_fen(exp_fen), is_white_turn): safe_moves.append(move)
	return safe_moves

def get_fen_offset_index(is_white_turn : bool, from_index : int, row_offset : int, col_offset : int) -> int | None:
	row, col = get_fen_row_col(from_index)
	if is_white_turn:
		row_offset = row_offset * -1
		col_offset = col_offset * -1
	new_row = row + row_offset
	new_col = col + col_offset
	if new_row < 0 or \
		new_row > BOARD_SIZE -1: return None
	if new_col < 0 or \
		new_col > BOARD_SIZE -1: return None
	index = get_fen_index(new_row, new_col)
	return index

def get_fen_row_col(index: int) -> tuple[int,int]:
	row = index // BOARD_SIZE
	col = index - (row * BOARD_SIZE)
	return row, col

def get_fen_index(row : int , col : int) -> int:
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
	left = [(0, index) for index in range(BOARD_SIZE)]
	right = [(0, -index) for index in range(BOARD_SIZE)]
	up = [(index, 0) for index in range(BOARD_SIZE)]
	down = [(-index, 0) for index in range(BOARD_SIZE)]
	return up, down, right, left

def move_until_friendly(moves_offset : list[tuple[int,int]], from_index :int, exp_fen : list[str] , is_white_turn : bool) -> list[int]:
	moves = []
	for offset in moves_offset:
		move = get_fen_offset_index(is_white_turn, from_index, *offset)
		if move is None: continue
		if move == from_index: continue
		if exp_fen[move] == FEN.FEN_CHARS.BLANK_PIECE.value: moves.append(move)
		elif is_white_turn:
			if exp_fen[move].islower(): moves.append(move)
			break
		else: 
			if exp_fen[move].isupper(): moves.append(move)
			break
	return moves

def move_fixed_amount(moves_offset : list[tuple[int,int]], from_index :int, exp_fen : list[str] , is_white_turn : bool) -> list[int]:
	moves = []
	for offset in moves_offset:
		move = get_fen_offset_index(is_white_turn, from_index, *offset)
		if move is None: continue
		if exp_fen[move] == FEN.FEN_CHARS.BLANK_PIECE.value: moves.append(move)
		elif is_white_turn:
			if exp_fen[move].islower(): moves.append(move)
		else:
			if exp_fen[move].isupper(): moves.append(move)	
	return moves
# ------------------------



# -- Checking if Move is Valid --
def is_move_valid(from_index : int, dest_index: int, fen : FEN.Fen, is_white_turn : bool) -> bool:
	exp_fen = FEN.expand_fen(fen)
	if not is_from_valid(exp_fen[from_index], is_white_turn): return False
	if not is_side_valid(from_index, dest_index, exp_fen): return False
	if not is_dest_valid(from_index, dest_index, exp_fen, is_white_turn): return False
	return True

	# -- helpers --
def is_checkmate(exp_fen : list[int], is_white_turn, from_index : int, dest_index: int) -> bool:
	new_exp_fen = exp_fen
	new_exp_fen[dest_index] = new_exp_fen[from_index]
	new_exp_fen[from_index] = FEN.FEN_CHARS.BLANK_PIECE.value
	opponents_moves = get_opponent_available_moves(new_exp_fen, is_white_turn, use_getter = True)
	return len(opponents_moves) == 0

def get_opponent_available_moves(exp_fen : list[int], is_white_turn : bool, use_getter : bool = False) -> list[int]:
	moves = []
	is_same_side = lambda is_white_turn, fen_char : is_white_turn and fen_char.isupper() if is_white_turn else (not is_white_turn) and fen_char.islower()
	for index, fen_char in enumerate(exp_fen):
		if fen_char == FEN.FEN_CHARS.BLANK_PIECE.value: continue
		if is_same_side(is_white_turn, fen_char): continue
		piece_name = CHESS.get_name_from_fen(fen_char)
		if use_getter:
			moves += get_available_moves(piece_name, index, exp_fen, not is_white_turn)
		else:
			moves += CHESS.PIECES[piece_name].available_moves(index, exp_fen, not is_white_turn)
	return moves

def is_from_valid(from_piece : str, is_white_turn : bool) -> bool:
	if from_piece == FEN.FEN_CHARS.BLANK_PIECE.value: return False
	if not is_from_correct_side(from_piece, is_white_turn): return False
	return True 
def is_side_valid(from_index : int, dest_index : int, exp_fen : list[str]) -> bool:
	if is_same(from_index, dest_index): return False
	if is_same_team(exp_fen[from_index], exp_fen[dest_index]): return False
	return True 
def is_dest_valid(from_index : int, dest_index : int, exp_fen : list[str], is_white_turn : bool) -> bool:
	piece_name = CHESS.get_name_from_fen(exp_fen[from_index])
	available_moves = get_available_moves(piece_name, from_index, exp_fen, is_white_turn)
	if dest_index not in available_moves: return False
	return True
def is_king_safe(from_index : int, dest_index : int, fen : FEN.Fen, is_white_turn : bool) -> bool:
	new_exp_fen = FEN.expand_fen(fen)
	king_fen = 'K' if is_white_turn else 'k'
	
	# creating a copy of game state and making the move
	new_exp_fen[dest_index] = new_exp_fen[from_index]
	new_exp_fen[from_index] = FEN.FEN_CHARS.BLANK_PIECE.value

	opponents_moves = get_opponent_available_moves(new_exp_fen, is_white_turn)

	for move in opponents_moves:
		if new_exp_fen[move] == king_fen: return False

	return True
def is_from_correct_side(from_piece, is_white : bool) -> bool:
	if is_white: return from_piece.isupper()
	return from_piece.islower() 
def is_same(from_index : int, dest_index: int) -> bool:
	return from_index == dest_index
def is_same_team(piece1 : str, piece2: str) -> bool:
	if piece2 == FEN.FEN_CHARS.BLANK_PIECE.value: return False
	return piece1.islower() == piece2.islower()
# -------------------------------



