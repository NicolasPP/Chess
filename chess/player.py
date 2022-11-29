import pygame, enum, dataclasses, typing

from utils import asset as ASSETS
from utils import commands as CMD
from utils import FEN_notation as FENN
from chess import chess_data as CHESS
from chess import game as GAME

from config import *




# -- Enums --
class MOUSECLICK(enum.Enum):
	LEFT 		: int = 1
	MIDDLE 		: int = 2
	RIGHT 		: int = 3
	SCROLL_UP 	: int = 4
	SCROLL_DOWN : int = 5

class STATE(enum.Enum):
	PICK_PIECE 	: int = 0 #  picking a piece 
	DROP_PIECE 	: int = 1 # dropping the piece 
# -----------




# -- Classes --
@dataclasses.dataclass
class Player:
	side   : CHESS.SIDE
	board  : CHESS.Board
	pieces : dict[str, CHESS.Piece]
	turn   : bool
	state  : STATE = STATE.PICK_PIECE
'''
FIXEME : turn currently doesnt need to be a member,
	 	 maybe I'll need it later on so I wont remove it
'''

def PLAYER( *,
		side : CHESS.SIDE,
		piece_set : ASSETS.PIECE_SET,
		board_asset : ASSETS.BOARDS,
		scale : float,
	) -> Player:
	board = CHESS.get_board(board_asset.value, side, scale)
	pieces = CHESS.get_peices(piece_set.value, scale)
	player = Player( side, board, pieces, False )
	if side is CHESS.SIDE.WHITE:
		player.state = STATE.PICK_PIECE
		player.turn = True
	return player
# -------------




# -- Class Helpers --
def update_pieces_location( player : Player, fen : FENN.Fen ) -> None:
	CHESS.reset_board_grid( player.board )
	for piece, board_square in fen_to_piece_board_square( fen, player ):
		board_square.FEN_val = piece.FEN_val
		board_square.piece_surface = piece.sprite.surface.copy()
def next_state( player : Player ) -> None:
	next_state = player.state.value + 1
	state_amount = len( list(STATE) )
	player.state = STATE( next_state % state_amount )
# -------------------




# -- Render Board and Pieces --
def render_board( player : Player ) -> None:
	pygame.display.get_surface().blit( player.board.sprite.surface, player.board.pos_rect )
	if player.state is STATE.DROP_PIECE: show_available_moves( player )

def render_pieces( player : Player ) -> None:
	grid = player.board.grid
	board_offset = pygame.math.Vector2(player.board.pos_rect.topleft)
	picked = None
	if player.side is CHESS.SIDE.BLACK: grid = grid[::-1]
	for board_square in grid:
		if board_square.FEN_val is FEN.BLANK_PIECE: continue
		if board_square.picked_up:
			picked = board_square 
			continue
		assert board_square.piece_surface is not NO_SURFACE
		pygame.display.get_surface().blit( 
			board_square.piece_surface, 
			get_piece_render_pos( board_square, board_offset )
			)

	if picked is not None:
		if picked.piece_surface is NO_SURFACE: return
		pygame.display.get_surface().blit( 
			picked.piece_surface, 
			get_picked_up_render_pos( picked, board_offset )
			)

def show_available_moves( player ) -> None:
	picked = CHESS.get_picked_up( player.board )
	# if not player.turn: return
	if player.side is CHESS.SIDE.WHITE:
		if picked.FEN_val.islower(): return
	if player.side is CHESS.SIDE.BLACK:
		if picked.FEN_val.isupper(): return
	board_offset = pygame.math.Vector2(player.board.pos_rect.topleft)
	for surface, pos in CHESS.get_available_surface( picked, player.board):
		pygame.display.get_surface().blit(surface, pos)
# -----------------------------




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
	return piece_pos

def get_picked_up_render_pos( board_square : CHESS.Board_Square, board_offset : pygame.math.Vector2 ) -> tuple[float, float]:
	assert board_square.piece_surface is not NO_SURFACE
	piece_pos = get_piece_render_pos(board_square, board_offset)
	piece_rect = board_square.piece_surface.get_rect(topleft = board_square.rect.topleft)
	piece_rect.midbottom = pygame.mouse.get_pos()
	piece_pos = piece_rect.x, piece_rect.y
	return piece_pos
# ---------------




# -- player input --
def parse_player_input( 
	event : pygame.event.Event, 
	player : Player,
	fen : FENN.Fen,
	network,
	) -> None:
	if event.type == pygame.MOUSEBUTTONDOWN:
		if event.button == MOUSECLICK.LEFT.value: handle_mouse_down_left( player, fen )
	if event.type == pygame.MOUSEBUTTONUP:
		if event.button == MOUSECLICK.LEFT.value: handle_mouse_up_left( player, network, fen )
		
def board_collided_rects( player : Player 
	) -> typing.Generator[CHESS.Board_Square, None, None]:
	board_offset = pygame.math.Vector2(player.board.pos_rect.topleft)
	for board_square in player.board.grid:
		rect = board_square.rect.copy()
		topleft = board_offset + pygame.math.Vector2(rect.topleft)
		rect.topleft = int(topleft.x), int(topleft.y)
		if rect.collidepoint( pygame.mouse.get_pos() ):
			yield board_square

def handle_mouse_down_left( player : Player, fen : FENN.Fen ) -> None:
	for board_square in board_collided_rects( player ):
		if player.state is not STATE.PICK_PIECE: return
		if board_square.FEN_val is FEN.BLANK_PIECE: return 
		CHESS.set_picked_up( board_square, player.board, fen, player.side )
		next_state( player )


def handle_mouse_up_left( player : Player, network, fen) -> None:
	if player.state is not STATE.DROP_PIECE: return
	for board_square in board_collided_rects( player ):
		CHESS.reset_board_grid( player.board )
		from_coords = CHESS.get_picked_up(player.board).AN_coordinates
		dest_coords = board_square.AN_coordinates

		# send server move info and update pieces location
		fen.notation = network.send(CMD.move( from_coords, dest_coords, player.side.name ).info)
		update_pieces_location( player, fen )

	next_state( player )
	CHESS.reset_picked_up( player.board )
# ------------------

