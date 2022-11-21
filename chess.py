import pygame, string
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Generator

import asset as ASSETS
from config import *


# -- Classes --
@dataclass
class Board_Square:
	rect 				: pygame.rect.Rect
	AN_coordinates	 	: str 
	piece_surface 		: None | pygame.Surface = NO_SURFACE
	FEN_val 			: str = FEN_BLANK
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
class Piece_Info(Enum):
	P 	: int =  0
	N 	: int =  1
	R	: int =  2
	B 	: int =  3
	Q 	: int =  4
	K 	: int =  5

class SIDE(Enum):
	WHITE : int = 0
	BLACK : int = 1
# -----------

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
	''' get fen value from name of Piece_Info(Enum) '''
	get_white_fen = lambda name : name
	get_black_fen = lambda name : name.lower()

	for i in range( len(white_sprites) ):
		white_fen : str = get_white_fen(Piece_Info(i).name)
		black_fen : str = get_black_fen(Piece_Info(i).name)
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
		board_square.FEN_val = FEN_BLANK
		board_square.piece_surface = NO_SURFACE
# ------------------- 


# -- Checking if Move is Valid --
def is_move_valid(
	from_square : Board_Square,
	dest_square : Board_Square,
	game_FEN 	: str 
	) -> bool:
	return True
# -------------------------------

