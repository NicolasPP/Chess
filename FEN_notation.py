import string
from dataclasses import dataclass
from typing import Generator

from config import *


@dataclass
class Fen:
	notation : str = FEN.GAME_START_FEN

def iterate_FEN( fen : Fen ) -> Generator[str, None, None]:
	for fen_row in fen.notation.split(FEN.SPLIT):
		for piece_fen in fen_row: yield piece_fen 

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

def pack_fen( unpacked_fen : list[str] ) -> Fen:
	fen, blank_count = set_blank_fen(Fen(FEN.BLANK))
	for index in range(len( unpacked_fen )):
		if index % BOARD_SIZE == 0 and index > 0:
			fen, blank_count = set_blank_fen( fen, blank_count) 
			fen.notation += FEN.SPLIT
		if unpacked_fen[index] == FEN.BLANK_PIECE: blank_count += 1
		else:
			fen, blank_count = set_blank_fen( fen, blank_count) 
			fen.notation += unpacked_fen[index]
	return fen

def make_move( from_coords, dest_coords, fen : Fen ) -> None:
	expanded_fen = expand_fen(fen)
	expanded_fen[fen_index(dest_coords)] = expanded_fen[fen_index(from_coords)]
	expanded_fen[fen_index(from_coords)] = FEN.BLANK_PIECE
	return pack_fen( expanded_fen )

def fen_index( AN_coords ) -> int:
	return ((BOARD_SIZE - int(AN_coords[0])) * BOARD_SIZE) + string.ascii_lowercase.index(AN_coords[1])

