import pygame
from dataclasses import dataclass
import asset as ASSETS

from enum import Enum
from typing import Callable

from config import *

# -- Classes and Enums --
@dataclass
class Board:
	sprite 		: ASSETS.Sprite
	pos_rect 	: pygame.rect.Rect
	grid 		: list[pygame.rect.Rect]

@dataclass
class Piece:
	sprite 		: ASSETS.Sprite
	FEN_val 	: str
	valid_move 	: Callable = lambda : False
	is_white 	: Callable = lambda piece : piece.FEN_val.islower()
	is_black	: Callable = lambda piece : piece.FEN_val.isupper()

@dataclass
class Game:
	board 			: Board
	pieces 			: list[Piece]
	FEN_notation 	: str
	surface 		: pygame.Surface


class Piece_Info(Enum):
	PAWN 	: int =  0
	KNIGHT 	: int =  1
	ROOK 	: int =  2
	BISHOP 	: int =  3
	QUEEN 	: int =  4
	KING 	: int =  5
# -----------------------


# -- Get Game Object --
def GAME( 
	*,
	board_asset : ASSETS.BOARDS,
	piece_set : ASSETS.PIECE_SET,
	scale : float,
	fen_notation : str = GAME_START_FEN
	) -> Game:
	board = get_board(board_asset.value, scale)
	pieces = get_peices(piece_set.value, scale)
	board_surface = pygame.Surface(board.sprite.surface.get_size())
	return Game(board, pieces, fen_notation)
# --------------------- 

# -- Creating Game Object -- 
def get_grid_surface_size( board_sprite : ASSETS.Sprite) -> pygame.math.Vector2:
	offset = pygame.math.Vector2(GRID_OFFSET) * board_sprite.factor
	board_size = pygame.math.Vector2(board_sprite.surface.get_size())
	return board_size - (offset * 2)

def board_index_gen():
	for row in range(BOARD_SIZE):
		for col in range(BOARD_SIZE):
			yield row, col

def get_board(board_asset : ASSETS.Asset, scale : float) -> Board:
	sprite = ASSETS.load_board(board_asset, scale)
	pos_rect = sprite.surface.get_rect()
	grid = create_grid(sprite, pos_rect)
	return Board(sprite, pos_rect, grid)

def get_peices(piece_set : ASSETS.Piece_Set, scale : float) -> list[Piece]: 
	white_sprites, black_sprites = ASSETS.load_piece_set(piece_set, scale)
	assert len(white_sprites) == len(black_sprites)
	pieces = []
	''' get fen value from name of Piece_Info(Enum) '''
	get_white_fen = lambda name : name[0].lower()
	get_black_fen = lambda name : name[0]

	for i in range( len(white_sprites) ):
		pieces.append( Piece(white_sprites[i] , get_white_fen(Piece_Info(i).name)) )
		pieces.append( Piece(black_sprites[i] , get_black_fen(Piece_Info(i).name)) )

	return pieces

def create_grid(board_sprite : ASSETS.Sprite, pos_rect : pygame.rect.Rect) -> list[pygame.rect.Rect]:
	grid = []
	size = get_grid_surface_size(board_sprite) / BOARD_SIZE
	board_offset = pygame.math.Vector2(pos_rect.topleft)
	grid_offset = pygame.math.Vector2(GRID_OFFSET) * board_sprite.factor
	for row, col in board_index_gen():
		pos = pygame.math.Vector2(col * size.x, row * size.y)
		grid.append(pygame.rect.Rect(pos + board_offset + grid_offset, size))
	return grid
# --------------------------




# -- Tests --
def test_grid( grid : list[pygame.rect.Rect]) -> None:
	for rect in grid:
		surface = pygame.Surface(rect.size)
		surface.set_alpha(30)
		surface.fill('red')
		pygame.display.get_surface().blit(surface, rect)
# -----------


