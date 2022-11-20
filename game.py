import pygame, string
from dataclasses import dataclass
from config import * 
from typing import Generator
from enum import Enum 
import player as PLAYER
import chess as CHESS
import commands as CMD


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
def iterate_FEN( game : Game ):
	for fen_row in game.FEN_notation.split(FEN_SPLIT):
		for piece_fen in fen_row: yield piece_fen 

def decode_game_FEN( game : Game, player : PLAYER.Player
	)-> Generator[tuple[CHESS.Piece, pygame.rect.Rect], None, None]:
	count = 0
	for piece_fen in iterate_FEN( game ):
		if piece_fen.isnumeric(): count += int( piece_fen ) -1
		else: yield player.pieces[piece_fen], player.board.grid[count]
		count += 1

def set_blank_fen( fen_notation : str, blank_count : int) -> tuple[str, int]:
	if blank_count > 0:
		fen_notation += str(blank_count)
		blank_count = 0
	return fen_notation, blank_count

def expand_fen( game : Game, fen = '' ) -> str:
	for piece_fen in iterate_FEN( game ):
		if piece_fen.isnumeric(): fen += (int( piece_fen ) * FEN_BLANK)
		elif piece_fen == FEN_SPLIT: continue
		else: fen += piece_fen
	return list(fen)

def format_expanded_fen( unpacked_fen ) -> str:
	FEN_notation, blank_count = set_blank_fen( '', 0)
	for index in range(len( unpacked_fen )):
		if index % BOARD_SIZE == 0 and index > 0:
			FEN_notation, blank_count = set_blank_fen( FEN_notation, blank_count) 
			FEN_notation += FEN_SPLIT
		if unpacked_fen[index] == FEN_BLANK: blank_count += 1
		else:
			FEN_notation, blank_count = set_blank_fen( FEN_notation, blank_count) 
			FEN_notation += unpacked_fen[index]

	return FEN_notation

def process_move( command : CMD.Move, game : Game):
	index = lambda fen : ((BOARD_SIZE - int(fen[0])) * BOARD_SIZE) + string.ascii_lowercase.index(fen[1])
	dest_c, from_c = command.dest_coords, command.from_coords
	expanded_fen = expand_fen(game)
	expanded_fen[index(dest_c)] = expanded_fen[index(from_c)]
	expanded_fen[index(from_c)] = FEN_BLANK
	game.FEN_notation = format_expanded_fen( expanded_fen )
# ------------------



# -- Game Render and Update --
def render_board( game : Game, player : PLAYER.Player ) -> None:
	pygame.display.get_surface().blit( player.board.sprite.surface, player.board.pos_rect )

def render_pieces( game : Game, player : PLAYER.Player ) -> None:
	grid = player.board.grid
	if player.side is CHESS.SIDE.BLACK: grid = grid[::-1]
	for board_square in grid:
		if not board_square.FEN_val: continue
		pygame.display.get_surface().blit( 
			board_square.piece_surface, 
			get_piece_render_pos( board_square, player )
			)

def update_pieces_location( game, player ) -> None:
	board_offset = pygame.math.Vector2(player.board.pos_rect.topleft)
	for board_square in player.board.grid:
		board_square.FEN_val = ''
		board_square.piece_surface = None
	for piece, board_square in decode_game_FEN( game, player ):
		board_square.FEN_val = piece.FEN_val
		board_square.piece_surface = piece.sprite.surface.copy()
# ----------------------------

def get_piece_render_pos( board_square : CHESS.Board_Square, player : PLAYER.Player ) -> tuple[int, int]:
	board_offset = pygame.math.Vector2(player.board.pos_rect.topleft)
	piece_rect = board_square.piece_surface.get_rect(topleft = board_square.rect.topleft)
	piece_rect.bottom = board_square.rect.bottom
	piece_pos = pygame.math.Vector2(piece_rect.x, piece_rect.y) + board_offset
	if board_square.picked_up: 
		piece_rect.midbottom = pygame.mouse.get_pos()
		piece_pos = piece_rect.x, piece_rect.y
	return piece_pos


def exec_player_command( game : Game, *players: PLAYER.Player  ) -> None:
	command = CMD.get_command()
	if command is None: return
	process_move(command, game)
	next_turn( *players )
	for player in players: update_pieces_location( game, player )


def next_turn( *players : PLAYER.Player  ) -> None:
	for player in players: player.turn = not player.turn
	p1, p2 = players
	assert p1.turn != p2.turn
