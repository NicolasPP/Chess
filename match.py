import pygame, string
from dataclasses import dataclass
from typing import Callable
from config import *

import asset as ASSETS
import player as PLAYER
import FEN_notation as FENN
import chess as CHESS
import commands as CMD

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
	CMD.send_to( CMD.PLAYER, CMD.update_pieces_pos() )
	return match


def process_move( command : CMD.Command, match : Match):
	index = lambda fen : ((BOARD_SIZE - int(fen[0])) * BOARD_SIZE) + string.ascii_lowercase.index(fen[1])
	from_c, dest_c = command.info.split(CMD.C_SPLIT)
	expanded_fen = FENN.expand_fen(match.fen)
	expanded_fen[index(dest_c)] = expanded_fen[index(from_c)]
	expanded_fen[index(from_c)] = FEN.BLANK_PIECE
	match.fen = FENN.format_expanded_fen( expanded_fen )


def exec_player_command( match : Match) -> None:
	command = CMD.read_from(CMD.MATCH)
	if command is None: return
	process_move(command, match)
	CMD.send_to( CMD.PLAYER, CMD.next_turn() )
	CMD.send_to( CMD.PLAYER, CMD.update_pieces_pos() )

	