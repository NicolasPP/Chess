import enum

import chess.chess_data as CHESS
import chess.game as GAME
import utils.algebraic_notation as AN
import utils.FEN_notation as FEN
import utils.commands as CMD
from config import *


class MoveType(enum.Enum):
    CHECK = enum.auto()
    CHECKMATE = enum.auto()
    CASTLE = enum.auto()
    EN_PASSANT = enum.auto()
    REGULAR = enum.auto()
    INVALID = enum.auto()


# -- Classes --
class Match:
    def __init__(self):
        self.fen: FEN.Fen = FEN.Fen()
        self.moves: list[str] = []
        self.commands: list[str] = []
        self.update_pos: bool = False
        CMD.send_to(CMD.PLAYER, CMD.get(CMD.COMMANDS.UPDATE_POS))

    def process_local_move(self) -> None:
        command = CMD.read_from(CMD.MATCH)
        if command is None: return
        match (self.process_move(command.info)):
            case MoveType.CHECK:
                CMD.send_to(CMD.PLAYER, CMD.get(CMD.COMMANDS.UPDATE_POS))
            case MoveType.CHECKMATE:
                CMD.send_to(CMD.PLAYER, CMD.get(CMD.COMMANDS.UPDATE_POS))
                CMD.send_to(CMD.PLAYER, CMD.get(CMD.COMMANDS.END_GAME))
            case MoveType.CASTLE:
                pass
            case MoveType.EN_PASSANT:
                pass
            case MoveType.REGULAR:
                CMD.send_to(CMD.PLAYER, CMD.get(CMD.COMMANDS.UPDATE_POS))
            case MoveType.INVALID:
                CMD.send_to(CMD.PLAYER, CMD.get(CMD.COMMANDS.INVALID_MOVE))

    def process_move(self, command_info: str) -> MoveType:
        fc, dc, cmd_dest = command_info.split(I_SPLIT)
        from_index, dest_index = AN.get_index_from_an(*fc), AN.get_index_from_an(*dc)
        if not is_command_destination_valid(cmd_dest, self.fen.is_white_turn()) or \
            not GAME.is_move_valid(from_index, dest_index, self.fen): return MoveType.INVALID
        self.fen.make_move(from_index, dest_index)
        self.moves.append(command_info)

        c_fen = FEN.Fen(FEN.encode_fen_data(self.fen.data))
        c_fen.data.active_color = self.fen.get_next_active_color()
        move_type = get_move_type(c_fen)
        return move_type


# -------------

# -- Match Helpers --
def is_command_destination_valid(cmd_dest: str, is_white: bool) -> bool:
    if cmd_dest == CHESS.SIDE.WHITE.name and is_white: return True
    if cmd_dest == CHESS.SIDE.BLACK.name and not is_white: return True
    return False


def get_move_type(fen: FEN.Fen) -> MoveType:
    if GAME.is_opponent_in_checkmate(fen): return MoveType.CHECKMATE
    if GAME.is_opponent_in_check(fen): return MoveType.CHECK
    return MoveType.REGULAR
# -------------------------
