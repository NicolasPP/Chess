import pygame
from dataclasses import dataclass
import asset as ASSETS

from typing import Callable

from config import *

# -- Classes --
@dataclass
class Board:
	sprite : ASSETS.Sprite
	pos_rect : pygame.rect.Rect
	grid 	: list[pygame.rect.Rect]

@dataclass
class Piece:
	sprite : ASSETS.Sprite
	FEN_val : str
	valid_move : Callable = lambda : False

@dataclass
class Game:
	board : Board
	pieces : list[Piece]
	FEN_notation : str
# -------------




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
	pos_rect.center = pygame.math.Vector2(pygame.display.get_surface().get_size()) / 2
	grid = create_grid(sprite, pos_rect)
	return Board(sprite, pos_rect, grid)

def get_peices(piece_set : ASSETS.Piece_Set, scale : float) -> list[Piece]: 
	white_sprites, black_sprites = ASSETS.load_piece_set(piece_set, scale)
	return white_sprites, black_sprites

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



