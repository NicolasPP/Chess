import pygame, string
from dataclasses import dataclass
from typing import Callable
import asset as ASSETS
import player as PLAYER
import FEN_notation as FENN
import chess as CHESS
import commands as CMD
from config import *

@dataclass
class Match:
	white_player 	: PLAYER.Player
	black_player 	: PLAYER.Player
	fen				: FENN.Fen
	moves		 	: list[str]
	get_turn_player : Callable = lambda match : match.white_player if match.white_player.turn \
												else match.black_player

def MATCH( *,
		white_piece_set : ASSETS.PIECE_SET,
		white_board_asset : ASSETS.BOARDS,
		black_piece_set : ASSETS.PIECE_SET,
		black_board_asset : ASSETS.BOARDS,
		scale : float,
		fen : FENN.Fen = FENN.Fen()
	) -> Match:
	white_player = PLAYER.PLAYER(
	side = CHESS.SIDE.WHITE,
	piece_set = white_piece_set,
	board_asset = white_board_asset,
	scale = scale
	)

	black_player = PLAYER.PLAYER(
	side = CHESS.SIDE.BLACK,
	piece_set = black_piece_set,
	board_asset = black_board_asset,
	scale = scale
	)
	match = Match( white_player, black_player, fen, [] )
	PLAYER.update_pieces_location(match.white_player, match.fen)
	PLAYER.update_pieces_location(match.black_player, match.fen)
	return match


def process_move( command : CMD.Move, match : Match):
	index = lambda fen : ((BOARD_SIZE - int(fen[0])) * BOARD_SIZE) + string.ascii_lowercase.index(fen[1])
	dest_c, from_c = command.dest_coords, command.from_coords
	expanded_fen = FENN.expand_fen(match.fen)
	expanded_fen[index(dest_c)] = expanded_fen[index(from_c)]
	expanded_fen[index(from_c)] = FEN.BLANK_PIECE
	match.fen = FENN.format_expanded_fen( expanded_fen )



def parse_match_input( match: Match, event : pygame.event.Event)->None:
	PLAYER.parse_player_input( event, match.white_player, match.fen.notation )
	PLAYER.parse_player_input( event, match.black_player, match.fen.notation )


def render( match ) ->None:
	player = match.get_turn_player( match )
	PLAYER.render_board( player )
	PLAYER.render_pieces( player )

def exec_player_command( match : Match) -> None:
	command = CMD.get_command()
	if command is None: return
	process_move(command, match)
	next_turn( match )
	PLAYER.update_pieces_location( match.white_player, match.fen )
	PLAYER.update_pieces_location( match.black_player, match.fen )



def next_turn( match ) -> None:
	match.white_player.turn = not match.white_player.turn
	match.black_player.turn = not match.black_player.turn
	assert match.white_player.turn != match.black_player.turn
	