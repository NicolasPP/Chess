import string, dataclasses, typing, enum

from config import *


class FEN_CHARS(enum.Enum):
	BLANK_PIECE 	: str = "@"
	SPLIT 			: str = '/'
	BLANK_FEN		: str = ''



@dataclasses.dataclass
class Fen: 	
	notation : str = GAME_START_FEN
	def __getitem__(self, AN_C : str) -> int:
		'''
		returns the index of the expanded fen
		which corresponds with the passed AN_C (algebraic notation coordinates)
		'''	
		col_num = int(AN_C[0])
		row_str = AN_C[1]
		ascii_str = string.ascii_lowercase
		return ((BOARD_SIZE - col_num) * BOARD_SIZE) + ascii_str.index(row_str)
		



# -- Fen Helpers -- 
def iterate_FEN(fen : Fen) -> typing.Generator[str, None, None]:
	for fen_row in fen.notation.split(FEN_CHARS.SPLIT.value):
		for piece_fen in fen_row: yield piece_fen 

def set_blank_fen(fen : Fen, blank_count : int = 0) -> tuple[Fen, int]:
	if blank_count > 0:
		fen.notation += str(blank_count)
		blank_count = 0
	return fen, blank_count

def expand_fen(fen : Fen, expanded_fen : str = FEN_CHARS.BLANK_FEN.value) -> list[str]:
	for piece_fen in iterate_FEN(fen):
		if piece_fen.isnumeric(): expanded_fen += (int(piece_fen) * FEN_CHARS.BLANK_PIECE.value)
		elif piece_fen == FEN_CHARS.SPLIT.value: continue
		else: expanded_fen += piece_fen
	
	return list(expanded_fen)

def pack_fen(unpacked_fen : list[str]) -> Fen:
	fen, blank_count = set_blank_fen(Fen(FEN_CHARS.BLANK_FEN.value))
	for index in range(len( unpacked_fen )):

		if index % BOARD_SIZE == 0 and index > 0:
			fen, blank_count = set_blank_fen(fen, blank_count) 
			fen.notation += FEN_CHARS.SPLIT.value

		if unpacked_fen[index] == FEN_CHARS.BLANK_PIECE.value: blank_count += 1
		else:
			fen, blank_count = set_blank_fen(fen, blank_count) 
			fen.notation += unpacked_fen[index]

		
		fen, blank_count = set_blank_fen(fen, blank_count) 
	return fen

def make_move(from_c : str, dest_c : str, fen : Fen) -> Fen:
	expanded_fen = expand_fen(fen)
	expanded_fen[fen[dest_c]] = expanded_fen[fen[from_c]]
	expanded_fen[fen[from_c]] = FEN_CHARS.BLANK_PIECE.value
	assert len(expanded_fen) == BOARD_SIZE * BOARD_SIZE
	return pack_fen(expanded_fen)
# -----------------



