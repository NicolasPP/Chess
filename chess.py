import pygame, string
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Generator

import asset as ASSETS
import FEN_notation as FENN

from config import *


# -- Classes --
@dataclass
class Board_Square:
	rect 				: pygame.rect.Rect
	AN_coordinates	 	: str 
	piece_surface 		: None | pygame.surface.Surface = NO_SURFACE
	FEN_val 			: str = FEN.BLANK_PIECE
	picked_up			: bool = False

@dataclass
class Board:
	sprite 		: ASSETS.Sprite
	pos_rect 	: pygame.rect.Rect
	grid 		: list[Board_Square]


@dataclass
class Piece:
	sprite 		: ASSETS.Sprite
	FEN_val 	: str
# -------------
# -- Enums --
class PIECES(Enum):
	PAWN	: int =  0
	KNIGHT 	: int =  1
	ROOK	: int =  2
	BISHOP 	: int =  3
	QUEEN 	: int =  4
	KING 	: int =  5

	def set_moves( self, func : Callable) -> None: self.available_moves : Callable = func
	def set_fen( self, FEN_val : str) -> None: self.FEN_val : str = FEN_val

class SIDE(Enum):
	WHITE : int = 0
	BLACK : int = 1
# -----------

# -- Defining Movement --
'''
this decorator creates a variable " self.available_moves() "
inside the Piece_Info(Enum) object passed.
The function will return all possible moves for that Piece 
'''
def set_info_for(piece : PIECES, FEN_val : str):
	def set_valid_move(get_moves : Callable):
		piece.set_moves(get_moves)
		piece.set_fen( FEN_val )
		return get_moves
	return set_valid_move

@set_info_for(PIECES.PAWN, 'P') 
def PAWN_available_moves(from_index : int, exp_fen : list[str]) -> list[str]:
	print(f'getting available moves for : {PIECES.PAWN.name}')

@set_info_for(PIECES.KNIGHT, 'N') 
def KNIGHT_available_moves(from_index : int, exp_fen : list[str]) -> list[str]:
	print(f'getting available moves for : {PIECES.KNIGHT.name}')

@set_info_for(PIECES.ROOK, 'R') 
def ROOK_available_moves(from_index : int, exp_fen : list[str]) -> list[str]:
	print(f'getting available moves for : {PIECES.ROOK.name}')

@set_info_for(PIECES.BISHOP, 'B') 
def BISHOP_available_moves(from_index : int, exp_fen : list[str]) -> list[str]:
	print(f'getting available moves for : {PIECES.BISHOP.name}')

@set_info_for(PIECES.QUEEN, 'Q') 
def QUENN_available_moves(from_index : int, exp_fen : list[str]) -> list[str]:
	print(f'getting available moves for : {PIECES.QUEEN.name}')

@set_info_for(PIECES.KING, 'K') 
def KING_available_moves(from_index : int, exp_fen : list[str]) -> list[str]:
	print(f'getting available moves for : {PIECES.KING.name}')
# -----------------------


# -- getting assets --
def get_grid_surface_size( board_sprite : ASSETS.Sprite) -> pygame.math.Vector2:
	offset = pygame.math.Vector2(GRID_OFFSET) * board_sprite.factor
	board_size = pygame.math.Vector2(board_sprite.surface.get_size())
	return board_size - (offset * 2)

def board_square_info( side ) -> Generator[tuple[int, int, str], None, None]:
	ranks = string.ascii_lowercase[:BOARD_SIZE]
	ranks = ranks[::-1] if side is SIDE.BLACK else ranks
	for row in range(BOARD_SIZE):
		for col, rank in zip( range(BOARD_SIZE), ranks ):
			num = BOARD_SIZE - row if side is SIDE.WHITE else row + 1
			AN_coordinates = str(num) + rank 
			yield row, col, AN_coordinates

def get_board(board_asset : ASSETS.Asset, side : SIDE, scale : float) -> Board:
	sprite = ASSETS.load_board(board_asset, scale)
	if side is SIDE.BLACK: sprite.surface = pygame.transform.flip(sprite.surface, True, True)

	pos_rect = sprite.surface.get_rect()
	grid = create_grid(sprite, pos_rect, side)
	return Board(sprite, pos_rect, grid)

def get_peices(piece_set : ASSETS.Piece_Set, scale : float) -> dict[str, Piece]: 
	white_sprites, black_sprites = ASSETS.load_piece_set(piece_set, scale)
	assert len(white_sprites) == len(black_sprites)
	pieces = {}
	''' get fen value from name of PIECES(Enum) '''

	for i in range( len(white_sprites) ):
		white_fen : str = PIECES(i).FEN_val
		black_fen : str = PIECES(i).FEN_val.lower()
		pieces[white_fen] = Piece(white_sprites[i], white_fen) 
		pieces[black_fen] = Piece(black_sprites[i], black_fen) 

	return pieces

def create_grid(board_sprite : ASSETS.Sprite, pos_rect : pygame.rect.Rect, side : SIDE) -> list[Board_Square]:
	grid = []
	size = get_grid_surface_size(board_sprite) / BOARD_SIZE
	board_offset = pygame.math.Vector2(pos_rect.topleft)
	grid_offset = pygame.math.Vector2(GRID_OFFSET) * board_sprite.factor
	for row, col, AN_cordinates in board_square_info( side ):
		pos = pygame.math.Vector2(col * size.x, row * size.y)
		rect = pygame.rect.Rect(pos + board_offset + grid_offset, size)
		grid.append( Board_Square(rect, AN_cordinates) )
	if side is SIDE.BLACK: grid = grid[::-1]
	return grid
# --------------------------


# -- Class Helpers -- 
def set_picked_up(board_square : Board_Square, board : Board) -> None:
	reset_picked_up( board )
	board_square.picked_up = True

def reset_picked_up( board : Board ) -> None:
	for sqr in board.grid: sqr.picked_up = False

def is_picked_up( board : Board) -> bool:
	for sqr in board.grid:
		if sqr.picked_up: return True
	return False

def get_picked_up( board : Board) -> Board_Square:
	for sqr in board.grid:
		if sqr.picked_up: return sqr
	raise Exception( ' no peices picked up ' )

def reset_board_grid( board : Board ):
	for board_square in board.grid:
		board_square.FEN_val = FEN.BLANK_PIECE
		board_square.piece_surface = NO_SURFACE
# ------------------- 


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
	PIECES[piece].available_moves(from_index, exp_fen)
	# if dest_index not in available_moves: return False
	return True 

def get_name_from_fen( FEN_val ) -> PIECES:
	for piece in list(PIECES):
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

