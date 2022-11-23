import pygame, string, enum, dataclasses, typing

import asset as ASSETS
import chess as CHESS
import commands as CMD
import FEN_notation as FENN

from config import *


class MOUSECLICK(enum.Enum):
	LEFT 		: int = 1
	MIDDLE 		: int = 2
	RIGHT 		: int = 3
	SCROLL_UP 	: int = 4
	SCROLL_DOWN : int = 5

class STATE(enum.Enum):
	PICK_PIECE 	: int = 0 #  picking a piece 
	DROP_PIECE 	: int = 1 # dropping the piece 


'''
FIXEME : turn currently doesnt need to be a member,
	 	 maybe I'll need it later on so I wont remove it
'''
@dataclasses.dataclass
class Player:
	side   : CHESS.SIDE
	board  : CHESS.Board
	pieces : dict[str, CHESS.Piece]
	turn   : bool
	state  : STATE = STATE.PICK_PIECE



def PLAYER( *,
		side : CHESS.SIDE,
		piece_set : ASSETS.PIECE_SET,
		board_asset : ASSETS.BOARDS,
		scale : float,
	) -> Player:
	board = get_board(board_asset.value, side, scale)
	pieces = get_peices(piece_set.value, scale)
	player = Player( side, board, pieces, False )
	if side is CHESS.SIDE.WHITE:
		player.state = STATE.PICK_PIECE
		player.turn = True
	return player

def next_state( player : Player ) -> None:
	next_state = player.state.value + 1
	state_amount = len( list(STATE) )
	player.state = STATE( next_state % state_amount )




# -- Game Render --
def render_board( player : Player ) -> None:
	pygame.display.get_surface().blit( player.board.sprite.surface, player.board.pos_rect )

def render_pieces( player : Player ) -> None:
	board_offset = pygame.math.Vector2(player.board.pos_rect.topleft)
	grid = player.board.grid
	if player.side is CHESS.SIDE.BLACK: grid = grid[::-1]
	for board_square in grid:
		if board_square.FEN_val is FEN.BLANK_PIECE: continue
		assert board_square.piece_surface is not NO_SURFACE
		pygame.display.get_surface().blit( 
			board_square.piece_surface, 
			get_piece_render_pos( board_square, board_offset )
			)
# -----------------



# -- getting assets --
def get_grid_surface_size( board_sprite : ASSETS.Sprite) -> pygame.math.Vector2:
	offset = pygame.math.Vector2(GRID_OFFSET) * board_sprite.factor
	board_size = pygame.math.Vector2(board_sprite.surface.get_size())
	return board_size - (offset * 2)

def board_square_info( side ) -> typing.Generator[tuple[int, int, str], None, None]:
	ranks = string.ascii_lowercase[:BOARD_SIZE]
	ranks = ranks[::-1] if side is  CHESS.SIDE.BLACK else ranks
	for row in range(BOARD_SIZE):
		for col, rank in zip( range(BOARD_SIZE), ranks ):
			num = BOARD_SIZE - row if side is  CHESS.SIDE.WHITE else row + 1
			AN_coordinates = str(num) + rank 
			yield row, col, AN_coordinates

def get_board(board_asset : ASSETS.Asset, side : CHESS.SIDE, scale : float) -> CHESS.Board:
	sprite = ASSETS.load_board(board_asset, scale)
	if side is CHESS.SIDE.BLACK: sprite.surface = pygame.transform.flip(sprite.surface, True, True)

	pos_rect = sprite.surface.get_rect()
	grid = create_grid(sprite, pos_rect, side)
	return  CHESS.Board(sprite, pos_rect, grid)

def get_peices(piece_set : ASSETS.Piece_Set, scale : float) -> dict[str,  CHESS.Piece]: 
	white_sprites, black_sprites = ASSETS.load_piece_set(piece_set, scale)
	assert len(white_sprites) == len(black_sprites)
	pieces = {}
	''' get fen value from name of PIECES(Enum) '''

	for i in range( len(white_sprites) ):
		white_fen : str = CHESS.PIECES(i).FEN_val
		black_fen : str = CHESS.PIECES(i).FEN_val.lower()
		pieces[white_fen] = CHESS.Piece(white_sprites[i], white_fen) 
		pieces[black_fen] = CHESS.Piece(black_sprites[i], black_fen) 

	return pieces

def create_grid(board_sprite : ASSETS.Sprite, pos_rect : pygame.rect.Rect, side :  CHESS.SIDE) -> list[ CHESS.Board_Square]:
	grid = []
	size = get_grid_surface_size(board_sprite) / BOARD_SIZE
	board_offset = pygame.math.Vector2(pos_rect.topleft)
	grid_offset = pygame.math.Vector2(GRID_OFFSET) * board_sprite.factor
	for row, col, AN_cordinates in board_square_info( side ):
		pos = pygame.math.Vector2(col * size.x, row * size.y)
		rect = pygame.rect.Rect(pos + board_offset + grid_offset, size)
		grid.append( CHESS.Board_Square(rect, AN_cordinates) )
	if side is  CHESS.SIDE.BLACK: grid = grid[::-1]
	return grid
# --------------------------




# -- Piece Pos --
def fen_to_piece_board_square( 
		fen : FENN.Fen, 
		player : Player
	)-> typing.Generator[tuple[CHESS.Piece, CHESS.Board_Square], None, None]:
	count = 0
	for piece_fen in FENN.iterate_FEN( fen ):
		if piece_fen.isnumeric(): count += int( piece_fen ) -1
		else: yield player.pieces[piece_fen], player.board.grid[count]
		count += 1

def get_piece_render_pos( board_square : CHESS.Board_Square, board_offset : pygame.math.Vector2 ) -> tuple[float, float]:
	assert board_square.piece_surface is not NO_SURFACE
	piece_rect = board_square.piece_surface.get_rect(topleft = board_square.rect.topleft)
	piece_rect.bottom = board_square.rect.bottom
	pos = pygame.math.Vector2(piece_rect.x, piece_rect.y) + board_offset
	piece_pos = pos.x, pos.y
	if board_square.picked_up: 
		piece_rect.midbottom = pygame.mouse.get_pos()
		piece_pos = piece_rect.x, piece_rect.y
	return piece_pos
# ---------------




# -- player input --
def parse_player_input( 
	event : pygame.event.Event, 
	player : Player,
	game_FEN : str
	) -> None:
	if event.type == pygame.MOUSEBUTTONDOWN:
		if event.button == MOUSECLICK.LEFT.value: handle_mouse_down_left( player )
	if event.type == pygame.MOUSEBUTTONUP:
		if event.button == MOUSECLICK.LEFT.value: handle_mouse_up_left( player, game_FEN )
		
def board_collided_rects( player : Player 
	) -> typing.Generator[tuple[CHESS.Board_Square,pygame.rect.Rect], None, None]:
	board_offset = pygame.math.Vector2(player.board.pos_rect.topleft)
	for board_square in player.board.grid:
		rect = board_square.rect.copy()
		topleft = board_offset + pygame.math.Vector2(rect.topleft)
		rect.topleft = int(topleft.x), int(topleft.y)
		if rect.collidepoint( pygame.mouse.get_pos() ):
			yield board_square, rect

def handle_mouse_down_left( player : Player ) -> None:
	for board_square, rect in board_collided_rects( player ):
		if player.state is not STATE.PICK_PIECE: return
		if board_square.FEN_val is FEN.BLANK_PIECE: return
		CHESS.set_picked_up( board_square, player.board )
		next_state( player )


def handle_mouse_up_left( player : Player, game_FEN : str) -> None:
	if player.state is not STATE.DROP_PIECE: return
	for board_square, rect in board_collided_rects( player ):
		CHESS.reset_board_grid( player.board )
		from_coords = CHESS.get_picked_up(player.board).AN_coordinates
		dest_coords = board_square.AN_coordinates
		CMD.send_to( CMD.MATCH, CMD.move( from_coords, dest_coords, player.side.name ) )
	next_state( player )
	CHESS.reset_picked_up( player.board )
# ------------------

# -- Exec Match Commands --
def next_turn( *players : Player ) -> None:
	for player in players: player.turn = not player.turn
	p1, p2 = players
	assert p1.turn != p2.turn

def update_pieces_location( player : Player, fen : FENN.Fen ) -> None:
	CHESS.reset_board_grid( player.board )
	for piece, board_square in fen_to_piece_board_square( fen, player ):
		board_square.FEN_val = piece.FEN_val
		board_square.piece_surface = piece.sprite.surface.copy()

def exec_match_command( white_player : Player, black_player : Player, fen: FENN.Fen ) -> None:
	command = CMD.read_from(CMD.PLAYER)
	if command is None: return
	if command.info == PLAYER_COMMANDS.UPDATE_POS:
		update_pieces_location( white_player, fen )
		update_pieces_location( black_player, fen )
	elif command.info == PLAYER_COMMANDS.NEXT_TURN:
		next_turn(white_player, black_player)
# -------------------------


