import pygame
from dataclasses import dataclass
from config import * 
from typing import Generator
import player as PLAYER
import chess as CHESS


@dataclass
class Game:
	FEN_notation : str


# -- Get Game Object --
def GAME( 
	*players : PLAYER.Player,
	fen_notation : str = GAME_START_FEN
	 ) -> Game:
	game = Game(fen_notation)
	for player in players: update_pieces_location( game, player)
	return game
# --------------------- 


# -- FEN notation --
def iterate_FEN( game : Game, player : PLAYER.Player ):
	for fen_row in game.FEN_notation.split('/'):
		for piece_fen in fen_row: yield piece_fen 

def decode_game_FEN( game : Game, player : PLAYER.Player
	)-> Generator[tuple[CHESS.Piece, pygame.rect.Rect], None, None]:
	count = 0
	for piece_fen in iterate_FEN( game, player ):
		if piece_fen.isnumeric(): count += int( piece_fen ) -1
		else: yield player.pieces[piece_fen], player.board.grid[count]
		count += 1
# ------------------



# -- Game Render and Update --
def render_board( game : Game, player : PLAYER.Player ) -> None:
	pygame.display.get_surface().blit( player.board.sprite.surface, player.board.pos_rect )

def render_pieces( game : Game, player : PLAYER.Player ) -> None:
	board_offset = pygame.math.Vector2(player.board.pos_rect.topleft)
	grid = player.board.grid
	if player.side is CHESS.SIDE.WHITE: grid = grid[::-1]
	for board_square in grid:
		if not board_square.FEN_val: continue
		piece_rect = board_square.piece_surface.get_rect(topleft = board_square.rect.topleft)
		piece_rect.bottom = board_square.rect.bottom
		peice_pos = pygame.math.Vector2(piece_rect.x, piece_rect.y)
		pygame.display.get_surface().blit( board_square.piece_surface, peice_pos + board_offset )

def update_pieces_location( game, player ) -> None:
	board_offset = pygame.math.Vector2(player.board.pos_rect.topleft)
	for piece, board_square in decode_game_FEN( game, player ):
		board_square.FEN_val = piece.FEN_val
		board_square.piece_surface = piece.sprite.surface.copy()

# ----------------------------


# -- player input --
def parse_player_input( 
	event : pygame.event.Event, 
	player : PLAYER.Player
	) -> None:
	board_offset = pygame.math.Vector2(player.board.pos_rect.topleft)
	mouse_pos = pygame.math.Vector2( pygame.mouse.get_pos() ) 
	if event.type == pygame.MOUSEBUTTONDOWN:
		for board_square in player.board.grid:
			rect = board_square.rect.copy()
			rect.topleft = board_offset + rect.topleft
			if rect.collidepoint( mouse_pos ):
				print( board_square.AN_coordinates )
# ------------------



# -- Tests --
def test_grid( player : PLAYER.Player) -> None:
	count = 0
	for board_square in player.board.grid:
		surface = pygame.Surface(board_square.rect.size)
		surface.set_alpha(30)
		surface.fill('red')
		pos = board_square.rect.x + player.board.pos_rect.x, board_square.rect.y + player.board.pos_rect.y
		pygame.display.get_surface().blit(surface, pos)
		count += 1 
# -----------



