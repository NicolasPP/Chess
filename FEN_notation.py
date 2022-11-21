from dataclasses import dataclass
from typing import Generator

from config import *
import chess as CHESS


@dataclass
class Fen:
	notation : str = FEN.GAME_START_FEN

def iterate_FEN( fen : Fen ) -> Generator[str, None, None]:
	for fen_row in fen.notation.split(FEN.SPLIT):
		for piece_fen in fen_row: yield piece_fen 

def decode_game_FEN( 
		fen : Fen, 
		player_pieces : dict[str, CHESS.Piece],
		player_grid   : list[CHESS.Board_Square]
	)-> Generator[tuple[CHESS.Piece, CHESS.Board_Square], None, None]:
	count = 0
	for piece_fen in iterate_FEN( fen ):
		if piece_fen.isnumeric(): count += int( piece_fen ) -1
		else: yield player_pieces[piece_fen], player_grid[count]
		count += 1

def set_blank_fen( fen : Fen = Fen(FEN.BLANK), blank_count : int = 0) -> tuple[Fen, int]:
	if blank_count > 0:
		fen.notation += str(blank_count)
		blank_count = 0
	return fen, blank_count

def expand_fen( fen : Fen, expanded_fen : str = FEN.BLANK ) -> list[str]:
	for piece_fen in iterate_FEN( fen ):
		if piece_fen.isnumeric(): expanded_fen += (int( piece_fen ) * FEN.BLANK_PIECE)
		elif piece_fen == FEN.SPLIT: continue
		else: expanded_fen += piece_fen
	return list(expanded_fen)

def format_expanded_fen( unpacked_fen : list[str] ) -> Fen:
	fen, blank_count = set_blank_fen(Fen(FEN.BLANK))
	print( fen.notation )
	for index in range(len( unpacked_fen )):
		if index % BOARD_SIZE == 0 and index > 0:
			fen, blank_count = set_blank_fen( fen, blank_count) 
			fen.notation += FEN.SPLIT
		if unpacked_fen[index] == FEN.BLANK_PIECE: blank_count += 1
		else:
			fen, blank_count = set_blank_fen( fen, blank_count) 
			fen.notation += unpacked_fen[index]
	print( fen.notation )
	return fen
