import pygame
from dataclasses import dataclass
from config import * 
from typing import Generator
import player as PLAYER
import chess as CHESS


@dataclass
class Game:
	FEN_notation 	: str


# -- Get Game Object --
def GAME( fen_notation : str = GAME_START_FEN ) -> Game:
	return Game(fen_notation)
# --------------------- 


# -- FEN notation --

def iterate_FEN( game : Game, player : PLAYER.Player ):
	fen = game.FEN_notation[::-1] if player.side is CHESS.SIDE.WHITE else game.FEN_notation
	for fen_row in fen.split('/'):
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
	for piece, rect in decode_game_FEN( game, player ):
		piece_rect = piece.sprite.surface.get_rect(topleft = rect.topleft)
		piece_rect.bottom = rect.bottom
		peice_pos = pygame.math.Vector2(piece_rect.x, piece_rect.y)
		pygame.display.get_surface().blit( piece.sprite.surface, peice_pos + board_offset )
# ----------------------------

# -- Tests --
def test_grid( player : PLAYER.Player) -> None:
	count = 0
	for rect in player.board.grid:
		surface = pygame.Surface(rect.size)
		surface.set_alpha(30)
		surface.fill('red')
		pos = rect.x + player.board.pos_rect.x, rect.y + player.board.pos_rect.y
		pygame.display.get_surface().blit(surface, pos)
		count += 1 
# -----------



