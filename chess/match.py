import enum

import chess.chess_data as CHESS
import chess.game as GAME
import utils.algebraic_notation as AN
import utils.Forsyth_Edwards_notation as FEN
import utils.commands as CMD
from config import *


class MoveTags(enum.Enum):
    CHECK = enum.auto()
    CHECKMATE = enum.auto()
    REGULAR = enum.auto()
    INVALID = enum.auto()
    TAKE = enum.auto()


# -- Classes --
class Match:
    def __init__(self):
        self.fen: FEN.Fen = FEN.Fen()
        self.moves: list[str] = []
        self.captured_pieces: str = ''
        self.commands: list[str] = []
        self.update_fen: bool = False
        CMD.send_to(CMD.PLAYER, CMD.get(CMD.COMMANDS.UPDATE_POS, self.fen.notation))

    def process_local_move(self) -> None:
        command = CMD.read_from(CMD.MATCH)
        if command is None: return
        match (self.process_move(command.info)):
            case MoveTags.CHECK:
                CMD.send_to(CMD.PLAYER, CMD.get(CMD.COMMANDS.UPDATE_POS, self.fen.notation))
            case MoveTags.CHECKMATE:
                CMD.send_to(CMD.PLAYER, CMD.get(CMD.COMMANDS.UPDATE_POS, self.fen.notation))
                CMD.send_to(CMD.PLAYER, CMD.get(CMD.COMMANDS.END_GAME))
            case MoveTags.REGULAR:
                CMD.send_to(CMD.PLAYER, CMD.get(CMD.COMMANDS.UPDATE_POS, self.fen.notation))
            case MoveTags.INVALID:
                CMD.send_to(CMD.PLAYER, CMD.get(CMD.COMMANDS.INVALID_MOVE))

    def process_move(self, command_info: str) -> list[MoveTags]:
        fc, dc, cmd_dest, target_fen = command_info.split(I_SPLIT)
        from_index, dest_index = AN.get_index_from_an(*fc), AN.get_index_from_an(*dc)
        if not is_command_destination_valid(cmd_dest, self.fen.is_white_turn()) or \
            not GAME.is_move_valid(from_index, dest_index, self.fen): return [MoveTags.INVALID]
        self.fen.make_move(from_index, dest_index, target_fen)
        self.moves.append(command_info)

        c_fen = FEN.Fen(FEN.encode_fen_data(self.fen.data))
        c_fen.data.active_color = self.fen.get_next_active_color()
        return get_move_tags(c_fen)


# -------------

# -- Match Helpers --
def is_command_destination_valid(cmd_dest: str, is_white: bool) -> bool:
    if cmd_dest == CHESS.SIDE.WHITE.name and is_white: return True
    if cmd_dest == CHESS.SIDE.BLACK.name and not is_white: return True
    return False


def get_move_tags(fen: FEN.Fen) -> list[MoveTags]:
    tags = []
    if GAME.is_opponent_in_checkmate(fen): tags.append(MoveTags.CHECKMATE)
    elif GAME.is_opponent_in_check(fen): tags.append(MoveTags.CHECK)
    else: tags.append(MoveTags.REGULAR)
    return tags
# -------------------------
