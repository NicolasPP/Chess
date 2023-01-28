import string, typing, enum

from config import *


class FEN_CHARS(enum.Enum):
	BLANK_PIECE 	: str = "@"
	SPLIT 			: str = '/'
	BLANK_FEN		: str = ''
	

class Fen:
	def __init__(self, default_fen = GAME_START_FEN):
		self.notation : str = default_fen
		self.expanded  : list[str] = self.get_expanded()
	
	def __getitem__(self, index : int) -> str:
			'''
			index from 0 - 63
			return fen val of piece on that index
			'''
			return self.expanded[index]

	def get_expanded(self) -> list[str]:
		expanded_fen : str = ''
		for piece_fen in self.iterate():
			if piece_fen.isnumeric(): expanded_fen += (int(piece_fen) * FEN_CHARS.BLANK_PIECE.value)
			elif piece_fen == FEN_CHARS.SPLIT.value: continue
			else: expanded_fen += piece_fen
		
		return list(expanded_fen)

	def iterate(self) -> typing.Generator[str, None, None]:
		for fen_row in self.notation.split(FEN_CHARS.SPLIT.value):
			for piece_fen in fen_row: yield piece_fen

	def make_move(self, from_index : int, dest_index : int) -> None:
		self.expanded[dest_index] = self.expanded[from_index]
		self.expanded[from_index] = FEN_CHARS.BLANK_PIECE.value
		self.notation = self.get_packed()
		assert len(self.expanded) == BOARD_SIZE * BOARD_SIZE

	def get_packed(self) -> None:
		fen, blank_count = set_blank_fen(Fen(FEN_CHARS.BLANK_FEN.value))
		for index in range(len(self.expanded)):
	
			if index % BOARD_SIZE == 0 and index > 0:
				fen, blank_count = set_blank_fen(fen, blank_count) 
				fen.notation += FEN_CHARS.SPLIT.value
	
			if self.expanded[index] == FEN_CHARS.BLANK_PIECE.value: blank_count += 1
			else:
				fen, blank_count = set_blank_fen(fen, blank_count) 
				fen.notation += self.expanded[index]
	
			
			fen, blank_count = set_blank_fen(fen, blank_count) 
		return fen.notation

	def get_notation(self) -> str: return self.notation


# -- Fen Helpers --
def get_index_from_ANC(algebraic_notation_coordinates : str) -> int:
	col_num = int(algebraic_notation_coordinates[0])
	row_str = algebraic_notation_coordinates[1]
	ascii_str = string.ascii_lowercase
	return ((BOARD_SIZE - col_num) * BOARD_SIZE) + ascii_str.index(row_str)

def set_blank_fen(fen : Fen, blank_count : int = 0) -> tuple[Fen, int]:
	if blank_count > 0:
		fen.notation += str(blank_count)
		blank_count = 0
	return fen, blank_count
# -----------------




