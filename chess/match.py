import dataclasses

from utils import FEN_notation as FENN
from utils import commands as CMD
from chess import chess_data as CHESS
from chess import game as GAME

from config import *




# -- Classes --
@dataclasses.dataclass
class Match:
	fen				: FENN.Fen
	moves		 	: list[str]

def MATCH( *,
		fen : FENN.Fen = FENN.Fen()
	) -> Match:
	CMD.send_to( CMD.PLAYER, CMD.update_pieces_pos() )
	fen = FENN.Fen()
	return Match(fen, [] )
# -------------




# -- Exec Match Commands --
def exec_player_command( match : Match) -> None:
	command = CMD.read_from(CMD.MATCH)
	if command is None: return
	process_local_move(command, match)

def process_local_move( command : CMD.Command, match : Match ) -> None:
	fc, dc, cmd_dest = command.info.split(C_SPLIT)
	if is_valid_command_dest(cmd_dest, is_white_turn(match)):
		if GAME.is_move_valid(match.fen[fc],match.fen[dc],FENN.expand_fen(match.fen),is_white_turn(match)):
			match.fen = FENN.make_move( command.info, match.fen )
			CMD.send_to( CMD.PLAYER, CMD.next_turn() )
			match.moves.append( command.info )
	CMD.send_to( CMD.PLAYER, CMD.update_pieces_pos() )


def process_move( command_info : str, match : Match ) -> bool:
	fc, dc, cmd_dest = command_info.split(C_SPLIT)
	if is_valid_command_dest(cmd_dest, is_white_turn(match)):
		if GAME.is_move_valid(match.fen[fc],match.fen[dc],FENN.expand_fen(match.fen),is_white_turn(match)):
			match.fen = FENN.make_move( command_info, match.fen )
			match.moves.append( command_info )
			return True
	return False


def is_white_turn( match : Match ):
	return len( match.moves ) % 2 == 0

def is_valid_command_dest( cmd_dest : str , is_white : bool) -> bool:
	if cmd_dest == CHESS.SIDE.WHITE.name and \
		is_white: return True
	if cmd_dest == CHESS.SIDE.BLACK.name and \
		not is_white: return True
	return False
# -------------------------



