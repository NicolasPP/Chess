import pygame
from dataclasses import dataclass
from enum import Enum
from config import *
from typing import Generator

import asset as ASSETS
import chess as CHESS
import commands as CMD
import FEN_notation as FENN


class MOUSECLICK(Enum):
	LEFT 		: int = 1
	MIDDLE 		: int = 2
	RIGHT 		: int = 3
	SCROLL_UP 	: int = 4
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




# -- Game Render and Update --
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
# ----------------------------




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
		topleft = board_offset + pygame.math.Vector2(rect.topleft)
		rect.topleft = int(topleft.x), int(topleft.y)
		if rect.collidepoint( pygame.mouse.get_pos() ):
			yield board_square, rect

def handle_mouse_down_left( player : Player ) -> None:
	for board_square, rect in board_collided_rects( player ):
		if not player.turn: return
		if player.state is not STATE.PICK_PIECE: return
		if board_square.FEN_val is FEN.BLANK_PIECE: return
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
		from_coords = CHESS.get_picked_up(player.board).AN_coordinates
		dest_coords = board_square.AN_coordinates
		CMD.send_to( CMD.MATCH, CMD.move( from_coords, dest_coords ) )
	next_state( player )
	CHESS.reset_picked_up( player.board )
# ------------------

def next_turn( *players : Player ) -> None:
	for player in players: player.turn = not player.turn
	p1, p2 = players
	assert p1.turn != p2.turn

def update_pieces_location( player : Player, fen : FENN.Fen ) -> None:
	CHESS.reset_board_grid( player.board )
	for piece, board_square in FENN.decode_game_FEN( fen, player.pieces, player.board.grid ):
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