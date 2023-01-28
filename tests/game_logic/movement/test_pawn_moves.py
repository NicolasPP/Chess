import pytest

from chess import game as GAME
from chess import chess_data as CHESS
from utils import FEN_notation as FEN


get_moves = lambda from_index, expanded_fen : CHESS.PIECES['PAWN'].available_moves(from_index, expanded_fen, True)

def test_first_turn_double_move(pawn_test_fen):
	from_index = 50
	assert len(get_moves(from_index, FEN.expand_fen(pawn_test_fen))) is 2

def test_firt_turn_double_move_and_possible_take(pawn_test_fen):
	from_index = 53
	assert len(get_moves(from_index, FEN.expand_fen(pawn_test_fen))) is 3 

def test_regular_move(pawn_test_fen):
	from_index = 41
	assert len(get_moves(from_index, FEN.expand_fen(pawn_test_fen))) is 1

def test_blocked_by_piece(pawn_test_fen):
	from_index = 26
	assert len(get_moves(from_index, FEN.expand_fen(pawn_test_fen))) is 0

def test_blocked_by_piece_and_possible_take(pawn_test_fen):
	from_index = 21
	assert len(get_moves(from_index, FEN.expand_fen(pawn_test_fen))) is 1

def test_first_turn_double_move_blocked(pawn_test_fen):
	from_index = 55
	assert len(get_moves(from_index, FEN.expand_fen(pawn_test_fen))) is 1

def test_first_turn_blocked(pawn_test_fen):
	from_index = 52
	assert len(get_moves(from_index, FEN.expand_fen(pawn_test_fen))) is 0