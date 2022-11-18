import pygame
from dataclasses import dataclass
import asset as ASSETS

from enum import Enum
from typing import Callable, Generator

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
	pieces 			: dict[str, Piece]
	FEN_notation 	: str


class Piece_Info(Enum):
	P 	: int =  0
	N 	: int =  1
	R	: int =  2
	B 	: int =  3
	Q 	: int =  4
	K 	: int =  5
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
	return Game(board, pieces, fen_notation)
# --------------------- 



# -- Game Render and Update --
def render( game : Game ) -> None:
	board_offset = pygame.math.Vector2(game.board.pos_rect.topleft)
	pygame.display.get_surface().blit( game.board.sprite.surface, game.board.pos_rect )
	for piece, rect in decode_game_FEN( game ):
		piece_rect = piece.sprite.surface.get_rect(topleft = rect.topleft)
		piece_rect.bottom = rect.bottom
		peice_pos = pygame.math.Vector2(piece_rect.x, piece_rect.y)
		pygame.display.get_surface().blit( piece.sprite.surface, peice_pos + board_offset )
# ----------------------------



# -- FEN notation --

def iterate_FEN( game ):
	for fen_row in game.FEN_notation.split('/'):
		for piece_fen in fen_row: yield piece_fen 

def decode_game_FEN( game : Game
	)-> Generator[tuple[Piece, pygame.rect.Rect], None, None]:
	count = 0
	for piece_fen in iterate_FEN( game ):
		if piece_fen.isnumeric(): count += int( piece_fen ) -1
		else: yield game.pieces[piece_fen], game.board.grid[count]
		count += 1

# ------------------




# -- Creating Game Object -- 
def get_grid_surface_size( board_sprite : ASSETS.Sprite) -> pygame.math.Vector2:
	offset = pygame.math.Vector2(GRID_OFFSET) * board_sprite.factor
	board_size = pygame.math.Vector2(board_sprite.surface.get_size())
	return board_size - (offset * 2)

def board_index_gen() -> Generator[tuple[int, int], None, None]:
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
	pieces = {}
	''' get fen value from name of Piece_Info(Enum) '''
	get_white_fen = lambda name : name.lower()
	get_black_fen = lambda name : name

	for i in range( len(white_sprites) ):
		white_fen = get_white_fen(Piece_Info(i).name)
		black_fen = get_black_fen(Piece_Info(i).name)
		pieces[white_fen] = Piece(white_sprites[i] , white_fen) 
		pieces[black_fen] = Piece(black_sprites[i] , black_fen) 

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
def test_grid( game : Game) -> None:
	count = 0
	for rect in game.board.grid:
		surface = pygame.Surface(rect.size)
		surface.set_alpha(30)
		surface.fill('red')
		pos = rect.x + game.board.pos_rect.x, rect.y + game.board.pos_rect.y
		pygame.display.get_surface().blit(surface, pos)
		count += 1 
# -----------

