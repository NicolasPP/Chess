import typing

from chess import chess_data as CHESS

from config import *




# -- Defining Movement --
'''
this decorator creates a variable " self.available_moves() "
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
def PAWN_available_moves(from_index : int, exp_fen : list[str]) -> list[str]:
	print(f'getting available moves for : {CHESS.PIECES.PAWN.name}')

@set_info_for(CHESS.PIECES.KNIGHT, 'N') 
def KNIGHT_available_moves(from_index : int, exp_fen : list[str]) -> list[str]:
	print(f'getting available moves for : {CHESS.PIECES.KNIGHT.name}')

@set_info_for(CHESS.PIECES.ROOK, 'R') 
def ROOK_available_moves(from_index : int, exp_fen : list[str]) -> list[str]:
	print(f'getting available moves for : {CHESS.PIECES.ROOK.name}')

@set_info_for(CHESS.PIECES.BISHOP, 'B') 
def BISHOP_available_moves(from_index : int, exp_fen : list[str]) -> list[str]:
	print(f'getting available moves for : {CHESS.PIECES.BISHOP.name}')

@set_info_for(CHESS.PIECES.QUEEN, 'Q') 
def QUENN_available_moves(from_index : int, exp_fen : list[str]) -> list[str]:
	print(f'getting available moves for : {CHESS.PIECES.QUEEN.name}')

@set_info_for(CHESS.PIECES.KING, 'K') 
def KING_available_moves(from_index : int, exp_fen : list[str]) -> list[str]:
	print(f'getting available moves for : {CHESS.PIECES.KING.name}')
# -----------------------




# -- Checking if Move is Valid --
def is_move_valid(from_index : int, dest_index: int, exp_fen : list[str], is_white_turn : bool) -> bool:
	if not is_from_valid(exp_fen[from_index], is_white_turn): return False
	if not is_side_valid(from_index, dest_index, exp_fen): return False
	if not is_dest_valid(from_index, dest_index, exp_fen): return False
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
def is_dest_valid(from_index : int, dest_index : int, exp_fen : list[str]) -> bool:
	piece = get_name_from_fen(exp_fen[from_index])
	CHESS.PIECES[piece].available_moves(from_index, exp_fen)
	# if dest_index not in available_moves: return False
	return True 

def get_name_from_fen( FEN_val ) -> str:
	for piece in list(CHESS.PIECES):
		if piece.FEN_val == FEN_val.upper(): return piece.name
	raise Exception( f'FEN_val : {FEN_val} not found' )
def is_from_correct_side( from_piece, is_white : bool):
	if is_white: return from_piece.isupper()
	return from_piece.islower() 
def is_same(from_index : int, dest_index: int) -> bool:
	return from_index == dest_index
def is_from_blank( from_piece : str) -> bool: return from_piece == FEN.BLANK_PIECE
def is_same_team( from_piece : str, dest_piece: str):
	if dest_piece == FEN.BLANK_PIECE: return False
	return from_piece.islower() == dest_piece.islower()
# -------------------------------



