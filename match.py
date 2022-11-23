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
	if is_valid_command_dest(command.info, is_white_turn(match)):
		if CHESS.is_move_valid( command.info, match.fen, is_white_turn( match )):
			match.fen = FENN.make_move( command.info, match.fen )
			CMD.send_to( CMD.PLAYER, CMD.next_turn() )
			match.moves.append( command.info )
	CMD.send_to( CMD.PLAYER, CMD.update_pieces_pos() )

def is_white_turn( match : Match ):
	return len( match.moves ) % 2 == 0

def is_valid_command_dest( cmd_info : str , is_white : bool) -> bool:
	fc, dc, command_dest = cmd_info.split(C_SPLIT)
	if command_dest == CHESS.SIDE.WHITE.name and \
		is_white: return True
	if command_dest == CHESS.SIDE.BLACK.name and \
		not is_white: return True
	return False