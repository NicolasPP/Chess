import pygame, string
from dataclasses import dataclass
from typing import Callable
from config import *

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

def exec_player_command( match : Match) -> None:
	command = CMD.read_from(CMD.MATCH)
	if command is None: return
	process_move(command, match)

# --
def process_move( command : CMD.Command, match : Match ) -> None:
	from_c, dest_c = command.info.split(CMD.C_SPLIT)
	if CHESS.is_move_valid( from_c, dest_c, match.fen, is_white_turn( match )):
		match.fen = FENN.make_move( from_c, dest_c, match.fen )
		CMD.send_to( CMD.PLAYER, CMD.next_turn() )
		match.moves.append( command.info )
	CMD.send_to( CMD.PLAYER, CMD.update_pieces_pos() )

def is_white_turn( match : Match ):
	return len( match.moves ) % 2 == 0

