import pygame, string
from dataclasses import dataclass
from typing import Callable
from config import *

import asset as ASSETS
import FEN_notation as FENN
import chess as CHESS
import commands as CMD

@dataclass
class Match:
	fen				: FENN.Fen
	moves		 	: list[str]

def MATCH( *,
		fen : FENN.Fen = FENN.Fen()
	) -> Match:
	CMD.send_to( CMD.PLAYER, CMD.update_pieces_pos() )
	return Match(fen, [] )


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

	