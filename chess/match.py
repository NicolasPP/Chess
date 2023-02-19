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
        move_tags = self.process_move(command.info)

        for tag in move_tags:
            self.process_tags(tag)

    def process_move(self, command_info: str) -> list[MoveTags]:
        fc, dc, cmd_dest, target_fen = command_info.split(I_SPLIT)
        from_index, dest_index = AN.get_index_from_an(*fc), AN.get_index_from_an(*dc)
        before_move_fen = FEN.Fen(FEN.encode_fen_data(self.fen.data))

        if not is_command_destination_valid(cmd_dest, self.fen.is_white_turn()) or \
            not GAME.is_move_valid(from_index, dest_index, self.fen): return [MoveTags.INVALID]

        self.fen.make_move(from_index, dest_index, target_fen)
        self.moves.append(command_info)

        return self.get_move_tags(before_move_fen, from_index, dest_index)

    def get_move_tags(self, before_move_fen: FEN.Fen, from_index: int, dest_index: int) -> list[MoveTags]:
        tags = []

        is_en_passant = before_move_fen.is_move_en_passant(from_index, dest_index)
        pawn_fen = 'p' if before_move_fen.is_white_turn() else 'P'
        if GAME.is_take(before_move_fen, dest_index, is_en_passant):
            if is_en_passant: self.captured_pieces += pawn_fen
            else: self.captured_pieces += before_move_fen[dest_index]
            tags.append(MoveTags.TAKE)

        if GAME.is_opponent_in_checkmate(self.fen, not self.fen.is_white_turn()): tags.append(MoveTags.CHECKMATE)
        elif GAME.is_opponent_in_check(self.fen, not self.fen.is_white_turn()): tags.append(MoveTags.CHECK)
        else: tags.append(MoveTags.REGULAR)

        return tags

    def process_tags(self, tag: MoveTags) -> None:
        match tag:
            case MoveTags.CHECK:
                CMD.send_to(CMD.PLAYER, CMD.get(CMD.COMMANDS.UPDATE_POS, self.fen.notation))
            case MoveTags.CHECKMATE:
                CMD.send_to(CMD.PLAYER, CMD.get(CMD.COMMANDS.UPDATE_POS, self.fen.notation))
                CMD.send_to(CMD.PLAYER, CMD.get(CMD.COMMANDS.END_GAME))
            case MoveTags.REGULAR:
                CMD.send_to(CMD.PLAYER, CMD.get(CMD.COMMANDS.UPDATE_POS, self.fen.notation))
            case MoveTags.INVALID:
                CMD.send_to(CMD.PLAYER, CMD.get(CMD.COMMANDS.INVALID_MOVE))
            case MoveTags.TAKE:
                CMD.send_to(CMD.PLAYER, CMD.get(CMD.COMMANDS.UPDATE_CAP_PIECES, self.captured_pieces))


# -------------

# -- Match Helpers --


def is_command_destination_valid(cmd_dest: str, is_white: bool) -> bool:
    if cmd_dest == CHESS.SIDE.WHITE.name and is_white: return True
    if cmd_dest == CHESS.SIDE.BLACK.name and not is_white: return True
    return False
# -------------------------
