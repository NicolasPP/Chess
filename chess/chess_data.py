import pygame, dataclasses, enum, typing, string

from utils import asset as ASSETS
from utils import FEN_notation as FENN

from config import *




# -- Enums --
class PIECES(enum.Enum):
	PAWN	: int =  0
	KNIGHT 	: int =  1
	ROOK	: int =  2
	BISHOP 	: int =  3
	QUEEN 	: int =  4
	KING 	: int =  5

	def set_moves( self, func : typing.Callable) -> None: 
		self.available_moves : typing.Callable = func
	def set_fen( self, FEN_val : str) -> None: 
		self.FEN_val : str = FEN_val

class SIDE(enum.Enum):
	WHITE : int = 0
	BLACK : int = 1
# -----------




# -- Classes --
@dataclasses.dataclass
class Board_Square:
	rect 				: pygame.rect.Rect
	AN_coordinates	 	: str 
	FEN_val 			: str = FEN.BLANK_PIECE
	picked_up			: bool = False
	picked_up_moves		: list[int] | None = NO_SURFACE

@dataclasses.dataclass
class Board:
	sprite 		: ASSETS.Sprite
	pos_rect 	: pygame.rect.Rect
	grid 		: list[Board_Square]


@dataclasses.dataclass
class Piece:
	sprite 		: ASSETS.Sprite
	FEN_val 	: str
# -------------




# -- Class Helpers -- 
def set_picked_up(board_square : Board_Square, board : Board, fen : FENN.Fen, p_side : SIDE) -> None:
	if board_square.FEN_val == FEN.BLANK_PIECE: return 
	reset_picked_up(board)
	exp_fen = FENN.expand_fen(fen)
	is_white_turn = True if p_side is SIDE.WHITE else False
	name = get_name_from_fen(board_square.FEN_val)
	moves = PIECES[name].available_moves(fen[board_square.AN_coordinates], exp_fen, is_white_turn)
	board_square.picked_up_moves = moves
	board_square.picked_up = True

def reset_picked_up(board : Board) -> None:
	for sqr in board.grid: 
		sqr.picked_up = False
		sqr.picked_up_moves = NO_SURFACE

def is_picked_up(board : Board) -> bool:
	for sqr in board.grid:
		if sqr.picked_up: return True
	return False

def get_picked_up(board : Board) -> Board_Square:
	for sqr in board.grid:
		if sqr.picked_up: return sqr
	raise Exception( ' no peices picked up ' )

def reset_board_grid(board : Board) -> None:
	for board_square in board.grid:
		board_square.picked_up_moves = NO_SURFACE

def get_collided_board_square(board : Board) -> Board_Square | None:
	board_offset = pygame.math.Vector2(board.pos_rect.topleft)
	for board_square in board.grid:
		rect = board_square.rect.copy()
		topleft = board_offset + pygame.math.Vector2(rect.topleft)
		rect.topleft = int(topleft.x), int(topleft.y)
		if rect.collidepoint( pygame.mouse.get_pos() ):
			return board_square
	return None

def get_name_from_fen(FEN_val : str) -> str:
	for piece in list(PIECES):
		if piece.FEN_val == FEN_val.upper(): return piece.name
	raise Exception(f'FEN_val : {FEN_val} not found')

def get_available_moves_surface( picked : Board_Square, board : Board
	) -> typing.Generator[tuple[pygame.surface.Surface, pygame.math.Vector2], None, None]:
	assert picked.picked_up_moves is not None
	board_offset = pygame.math.Vector2(board.pos_rect.topleft)
	for index in picked.picked_up_moves:
		board_square = board.grid[index]
		pos = pygame.math.Vector2(board_square.rect.topleft)
		available_surface = pygame.surface.Surface(board_square.rect.size)
		available_surface.fill(AVAILABLE_MOVE_COLOR)
		available_surface.set_alpha(AVAILABLE_ALPHA)
		yield available_surface, board_offset + pos

def get_piece_render_pos(board_square : Board_Square, board_offset : pygame.math.Vector2, pieces : dict[str, Piece]) -> tuple[float, float]:
	piece_surface = pieces.get(board_square.FEN_val).sprite.surface
	if board_square.picked_up: return get_picked_up_piece_render_pos(board_square, board_offset, piece_surface)
	return get_unpicked_piece_render_pos(board_square, board_offset, piece_surface)

def get_unpicked_piece_render_pos(board_square : Board_Square, board_offset : pygame.math.Vector2, piece_surface : pygame.surface.Surface) -> tuple[float, float]:
	piece_rect = piece_surface.get_rect(topleft = board_square.rect.topleft)
	piece_rect.bottom = board_square.rect.bottom
	pos = pygame.math.Vector2(piece_rect.x, piece_rect.y) + board_offset
	piece_pos = pos.x, pos.y
	return piece_pos

def get_picked_up_piece_render_pos(board_square : Board_Square, board_offset : pygame.math.Vector2, piece_surface : pygame.surface.Surface) -> tuple[float, float]:
	piece_pos = get_unpicked_piece_render_pos(board_square, board_offset, piece_surface)
	piece_rect = piece_surface.get_rect(topleft = board_square.rect.topleft)
	piece_rect.midbottom = pygame.mouse.get_pos()
	return piece_rect.x, piece_rect.y
# ------------------- 




# -- getting assets --
def get_grid_surface_size(board_sprite : ASSETS.Sprite) -> pygame.math.Vector2:
	offset = pygame.math.Vector2(GRID_OFFSET) * board_sprite.factor
	board_size = pygame.math.Vector2(board_sprite.surface.get_size())
	return board_size - (offset * 2)

def board_square_info(side : SIDE) -> typing.Generator[tuple[int, int, str], None, None]:
	ranks = string.ascii_lowercase[:BOARD_SIZE]
	ranks = ranks[::-1] if side is  SIDE.BLACK else ranks
	for row in range(BOARD_SIZE):
		for col, rank in zip( range(BOARD_SIZE), ranks ):
			num = BOARD_SIZE - row if side is  SIDE.WHITE else row + 1
			AN_coordinates = str(num) + rank 
			yield row, col, AN_coordinates

def get_board(board_asset : ASSETS.Asset, side : SIDE, scale : float) -> Board:
	sprite = ASSETS.load_board(board_asset, scale)
	if side is SIDE.BLACK: sprite.surface = pygame.transform.flip(sprite.surface, True, True)

	pos_rect = sprite.surface.get_rect()
	grid = create_grid(sprite, pos_rect, side)
	return  Board(sprite, pos_rect, grid)

def get_peices(piece_set : ASSETS.Piece_Set, scale : float) -> dict[str,  Piece]: 
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

def create_grid(board_sprite : ASSETS.Sprite, pos_rect : pygame.rect.Rect, side :  SIDE) -> list[ Board_Square]:
	grid = []
	size = get_grid_surface_size(board_sprite) / BOARD_SIZE
	board_offset = pygame.math.Vector2(pos_rect.topleft)
	grid_offset = pygame.math.Vector2(GRID_OFFSET) * board_sprite.factor
	for row, col, AN_cordinates in board_square_info(side):
		pos = pygame.math.Vector2(col * size.x, row * size.y)
		rect = pygame.rect.Rect(pos + board_offset + grid_offset, size)
		grid.append(Board_Square(rect, AN_cordinates))
	if side is  SIDE.BLACK: grid = grid[::-1]
	return grid
# --------------------------