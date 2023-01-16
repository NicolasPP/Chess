from utils import FEN_notation as FENN
from utils import commands as CMD
from chess import chess_data as CHESS
from chess import game as GAME

from config import *


# -- Classes --
class Match:
	def __init__(self):
		self.fen				: FENN.Fen = FENN.Fen()
		self.moves		 		: list[str] = []
		self.commands 			: list[str] = []
		self.update_pos			: bool = False
		CMD.send_to(CMD.PLAYER, CMD.get(CMD.COMMANDS.UPDATE_POS))

	def process_local_move(self) -> None:
		command = CMD.read_from(CMD.MATCH)
		if command is None: return
		if self.process_move(command.info): 
			CMD.send_to(CMD.PLAYER, CMD.get(CMD.COMMANDS.NEXT_TURN))
			CMD.send_to(CMD.PLAYER, CMD.get(CMD.COMMANDS.UPDATE_POS))
		else:
			CMD.send_to(CMD.PLAYER, CMD.get(CMD.COMMANDS.INVALID_MOVE))

	def process_move(self, command_info : str) -> bool:
		fc, dc, cmd_dest = command_info.split(I_SPLIT)
		if is_command_dest_valid(cmd_dest, self.is_white_turn()):
			if GAME.is_move_valid(self.fen[fc],self.fen[dc],FENN.expand_fen(self.fen),self.is_white_turn()):
				self.fen = FENN.make_move(command_info, self.fen)
				self.moves.append(command_info)
				return True
		return False

	def is_white_turn(self) -> bool: return len( self.moves ) % 2 == 0
# -------------


# -- Match Helpers --
def is_command_dest_valid(cmd_dest : str , is_white : bool) -> bool:
	if cmd_dest == CHESS.SIDE.WHITE.name and \
		is_white: return True
	if cmd_dest == CHESS.SIDE.BLACK.name and \
		not is_white: return True
	return False
# -------------------------



