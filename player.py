import pygame
from dataclasses import dataclass
from enum import Enum
from config import *
import chess as CHESS
from typing import Generator
import asset as ASSETS
import commands as CMD


class MOUSECLICK(Enum):
	LEFT : int = 1
	MIDDLE : int = 2
	RIGHT : int = 3
	SCROLL_UP : int = 4
	SCROLL_DOWN : int = 5

class STATE(Enum):
	PICK_PIECE 	: int = 0 #  picking a piece 
	DROP_PIECE 	: int = 1 # dropping the piece 

@dataclass
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
	board = CHESS.get_board(board_asset.value, side, scale)
	pieces = CHESS.get_peices(piece_set.value, scale)
	player = Player( side, board, pieces, False )
	if side is CHESS.SIDE.WHITE:
		player.state = STATE.PICK_PIECE
		player.turn = True
	return player

def next_state( player : Player ) -> None:
	next_state = player.state.value + 1
	state_amount = len( list(STATE) )
	player.state = STATE( next_state % state_amount )



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
	) -> Generator[tuple[CHESS.Board_Square,pygame.rect.Rect], None, None]:
	board_offset = pygame.math.Vector2(player.board.pos_rect.topleft)
	for board_square in player.board.grid:
		rect = board_square.rect.copy()
		rect.topleft = board_offset + rect.topleft
		if rect.collidepoint( pygame.mouse.get_pos() ):
			yield board_square, rect

def handle_mouse_down_left( player : Player ) -> None:
	for board_square, rect in board_collided_rects( player ):
		if not player.turn: return
		if player.state is not STATE.PICK_PIECE: return
		if not board_square.FEN_val: return
		if board_square.FEN_val.islower() and\
			player.side is CHESS.SIDE.WHITE: return
		if board_square.FEN_val.isupper() and\
			player.side is CHESS.SIDE.BLACK: return
		CHESS.set_picked_up( board_square, player.board )
		next_state( player )


def handle_mouse_up_left( player : Player, game_FEN : str) -> None:
	for board_square, rect in board_collided_rects( player ):
		if not player.turn: return
		if player.state is not STATE.DROP_PIECE: return
		if board_square.FEN_val.islower() and\
			player.side is CHESS.SIDE.BLACK: break
		if board_square.FEN_val.isupper() and\
			player.side is CHESS.SIDE.WHITE: break
		if not CHESS.is_picked_up( player.board ) : break
		if CHESS.is_move_valid(
			CHESS.get_picked_up( player.board ),
			board_square,game_FEN):
			move_command = CMD.Move( 
					CHESS.get_picked_up(player.board).AN_coordinates,
					board_square.AN_coordinates)
			CMD.send_command( move_command )
	next_state( player )

	CHESS.reset_picked_up( player.board )
# ------------------
