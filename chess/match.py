import enum
from utils import FEN_notation as FEN
from utils import commands as CMD
from chess import chess_data as CHESS
from chess import game as GAME

from config import *


class MOVE_TYPE(enum.Enum):
	CHECK = enum.auto()
	CHECKMATE = enum.auto()
	CASTLE = enum.auto()
	EN_PASSANT = enum.auto()
	REGULAR = enum.auto()
	INVALID = enum.auto()

# -- Classes --
class Match:
	def __init__(self):
		self.fen				: FEN.Fen = FEN.Fen()
		self.moves		 		: list[str] = []
		self.commands 			: list[str] = []
		self.update_pos			: bool = False
		CMD.send_to(CMD.PLAYER, CMD.get(CMD.COMMANDS.UPDATE_POS))

	def process_local_move(self) -> None:
		command = CMD.read_from(CMD.MATCH)
		if command is None: return
		match(self.process_move(command.info)):
			case MOVE_TYPE.CHECK:
				CMD.send_to(CMD.PLAYER, CMD.get(CMD.COMMANDS.NEXT_TURN))
				CMD.send_to(CMD.PLAYER, CMD.get(CMD.COMMANDS.UPDATE_POS))
				print('check')
			case MOVE_TYPE.CHECKMATE:
				print('checkmate')
				CMD.send_to(CMD.PLAYER, CMD.get(CMD.COMMANDS.UPDATE_POS))
			case MOVE_TYPE.CASTLE: pass
			case MOVE_TYPE.EN_PASSANT: pass
			case MOVE_TYPE.REGULAR:
				CMD.send_to(CMD.PLAYER, CMD.get(CMD.COMMANDS.NEXT_TURN))
				CMD.send_to(CMD.PLAYER, CMD.get(CMD.COMMANDS.UPDATE_POS))
			case MOVE_TYPE.INVALID:
				CMD.send_to(CMD.PLAYER, CMD.get(CMD.COMMANDS.INVALID_MOVE))


	def process_move(self, command_info : str) -> MOVE_TYPE:
		fc, dc, cmd_dest = command_info.split(I_SPLIT)
		from_index = FEN.get_index_from_ANC(fc)
		dest_index = FEN.get_index_from_ANC(dc)
		is_white_turn = self.is_white_turn()
		if is_command_dest_valid(cmd_dest, self.is_white_turn()):
			if GAME.is_move_valid(from_index, dest_index, self.fen, is_white_turn):
				self.fen.make_move(from_index, dest_index)
				self.moves.append(command_info)
				if GAME.is_checkmate(self.fen, is_white_turn): return MOVE_TYPE.CHECKMATE
				if GAME.is_check(self.fen, is_white_turn): return MOVE_TYPE.CHECK
				return MOVE_TYPE.REGULAR
		return MOVE_TYPE.INVALID

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



