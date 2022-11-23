import pygame, dataclasses, enum	

from config import *




# -- Classes and Enums --
class TYPE(enum.Enum):
	SPRITE 	: int = 0
	SHEET 	: int = 1

@dataclasses.dataclass
class Asset:
	file : str
	a_type : TYPE
	rows : int = 1
	cols : int = 6

@dataclasses.dataclass
class Sprite:
	surface : pygame.surface.Surface
	factor : float

@dataclasses.dataclass
class Piece_Set:
	white_asset : Asset
	black_asset : Asset 

class BOARDS(enum.Enum):
	PLAIN1 : Asset = Asset('assets/boards/board_plain_01.png', TYPE.SPRITE)
	PLAIN2 : Asset = Asset('assets/boards/board_plain_02.png', TYPE.SPRITE)
	PLAIN3 : Asset = Asset('assets/boards/board_plain_03.png', TYPE.SPRITE)
	PLAIN4 : Asset = Asset('assets/boards/board_plain_04.png', TYPE.SPRITE)

class PIECE_SET(enum.Enum):
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
def scale(surface : pygame.surface.Surface, factor : float) -> pygame.surface.Surface:
	size = pygame.math.Vector2(surface.get_size()) * factor
	return pygame.transform.scale(surface, (round(size.x), round(size.y)))

def sheet_surface_gen(asset : Asset, surface_size : pygame.math.Vector2):
	for r in range(asset.rows):
		for c in range(asset.cols):
			surface = pygame.surface.Surface(surface_size)
			surface.set_colorkey( PIECE_BG )
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
	surface = pygame.image.load(file).convert()
	surface = scale(surface, factor)
	return Sprite(surface, factor)
# ----------------------




# --  user will call these functions --
def load_board(asset : Asset, factor : float) -> Sprite:
	return load_sprite(asset.file, factor)

def load_piece_set( piece_set : Piece_Set, factor : float) -> tuple[list[Sprite], list[Sprite]]:
	return load_sprite_sheet(piece_set.white_asset, factor), load_sprite_sheet(piece_set.black_asset, factor)
# -------------------------------------



