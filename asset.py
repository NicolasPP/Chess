from dataclasses import dataclass	
from enum import Enum
import pygame

from config import *




# -- Classes and Enums --
class TYPE(Enum):
	SPRITE 	: int = 0
	SHEET 	: int = 1

@dataclass
class Asset:
	file : str
	a_type : TYPE
	rows : int = 1
	cols : int = 6

@dataclass
class Sprite:
	surface : pygame.Surface
	factor : float

@dataclass
class Piece_Set:
	white_asset : Asset
	black_asset : Asset 

class BOARDS(Enum):
	PLAIN1 : Asset = Asset('assets/boards/board_plain_01.png', TYPE.SPRITE)
	PLAIN2 : Asset = Asset('assets/boards/board_plain_02.png', TYPE.SPRITE)
	PLAIN3 : Asset = Asset('assets/boards/board_plain_03.png', TYPE.SPRITE)
	PLAIN4 : Asset = Asset('assets/boards/board_plain_04.png', TYPE.SPRITE)

class PIECE_SET(Enum):
	SIMPLE16x16 : Piece_Set = Piece_Set(
			white_asset = Asset('assets/pieces-16-16/WhitePieces_Simplified.png', TYPE.SHEET),
			black_asset = Asset('assets/pieces-16-16/BlackPieces_Simplified.png', TYPE.SHEET)
		)
	NORMAL16x16 : Piece_Set = Piece_Set(
			white_asset = Asset('assets/pieces-16-16/WhitePieces.png', TYPE.SHEET),
			black_asset = Asset('assets/pieces-16-16/BlackPieces.png', TYPE.SHEET)
		)
	NORMAL16x32 : Piece_Set = Piece_Set(
			white_asset = Asset('assets/pieces-16-32/WhitePieces-Sheet.png', TYPE.SHEET),
			black_asset = Asset('assets/pieces-16-32/BlackPieces-Sheet.png', TYPE.SHEET)
		)
# -----------------------




# -- helper functions --
def scale(surface : pygame.Surface, factor : float) -> pygame.Surface:
	size = pygame.math.Vector2(surface.get_size()) * factor
	return pygame.transform.scale(surface, (round(size.x), round(size.y)))

def sheet_surface_gen(asset : Asset, surface_size : tuple[int, int]):
	for r in range(asset.rows):
		for c in range(asset.cols):
			surface = pygame.Surface(surface_size).convert_alpha()
			index 	= pygame.math.Vector2(c, r).elementwise()
			yield surface, index

def load_sprite_sheet(asset : Asset, factor : float) -> list[Sprite]:
	sheet_sprite 		= load_sprite(asset.file, factor = 1)
	sheet_dimensions 	= pygame.math.Vector2(asset.cols, asset.rows)
	sheet_size 			= pygame.math.Vector2(sheet_sprite.surface.get_size()).elementwise()
	surface_size 		= sheet_size / sheet_dimensions
	
	sprites = []

	for surface, index in sheet_surface_gen( asset, surface_size ):
		surface.blit(sheet_sprite.surface, surface_size * index * -1)
		surface = scale(surface, factor)
		sprites.append(Sprite(surface, factor))

	return sprites

def load_sprite( file : str, factor : float ) -> Sprite:
	surface = pygame.image.load(file).convert_alpha()
	surface = scale(surface, factor)
	return Sprite(surface, factor)
# ----------------------




# --  user will call these functions --
def load_board(asset : Asset, factor : float) -> Sprite:
	return load_sprite(asset.file, factor)

def load_piece_set( piece_set : Piece_Set, factor : float) -> tuple[list[Sprite], list[Sprite]]:
	return load_sprite_sheet(piece_set.white_asset, factor), load_sprite_sheet(piece_set.black_asset, factor)
# -------------------------------------


