import enum

import src.chess.board as chess_board
import src.chess.validate_move as validate_move

from src.utils.algebraic_notation import get_index_from_an
from src.utils.forsyth_edwards_notation import encode_fen_data, Fen, FenChars
import src.utils.commands as command_manager
from src.config import *


class MoveTags(enum.Enum):
    CHECK = enum.auto()
    CHECKMATE = enum.auto()
    REGULAR = enum.auto()
    INVALID = enum.auto()
    TAKE = enum.auto()


class Match:
    def __init__(self):
        self.fen: Fen = Fen()
        self.moves: list[str] = []
        self.captured_pieces: str = ''
        self.commands: list[command_manager.Command] = []
        self.update_fen: bool = False
        command_manager.send_to(
            command_manager.PLAYER,
            command_manager.get(command_manager.COMMANDS.UPDATE_FEN, self.fen.notation)
        )

    def process_local_move(self) -> None:
        command = command_manager.read_from(command_manager.MATCH)
        if command is None: return
        move_tags = self.process_move(command.info)

        commands = []

        for tag in move_tags:
            commands.extend(self.process_tag(tag))

        list(map(lambda cmd: command_manager.send_to(command_manager.PLAYER, cmd), commands))

    def process_move(self, command_info: str) -> list[MoveTags]:
        fc, dc, cmd_dest, target_fen = command_info.split(I_SPLIT)
        from_index, dest_index = get_index_from_an(*fc), get_index_from_an(*dc)
        before_move_fen = Fen(encode_fen_data(self.fen.data))

        if not is_command_destination_valid(cmd_dest, self.fen.is_white_turn()) \
                or not validate_move.is_move_valid(from_index, dest_index, self.fen):
            return [MoveTags.INVALID]

        self.fen.make_move(from_index, dest_index, target_fen)
        self.moves.append(command_info)

        return self.get_move_tags(before_move_fen, from_index, dest_index)

    def get_move_tags(self, before_move_fen: Fen, from_index: int, dest_index: int) -> list[MoveTags]:
        tags = []

        is_en_passant = before_move_fen.is_move_en_passant(from_index, dest_index)
        is_castle = before_move_fen.is_move_castle(from_index, dest_index)
        pawn_fen = FenChars.DEFAULT_PAWN.get_piece_fen(before_move_fen.is_white_turn())

        if validate_move.is_take(before_move_fen, dest_index, is_en_passant, is_castle):
            if is_en_passant:
                self.captured_pieces += pawn_fen
            else:
                self.captured_pieces += before_move_fen[dest_index]
            tags.append(MoveTags.TAKE)

        if validate_move.is_opponent_in_checkmate(self.fen):
            tags.append(MoveTags.CHECKMATE)
        elif validate_move.is_opponent_in_check(self.fen, not self.fen.is_white_turn()):
            tags.append(MoveTags.CHECK)
        else:
            tags.append(MoveTags.REGULAR)

        return tags

    def process_tag(self, tag: MoveTags) -> list[command_manager.Command]:
        ext_commands = []
        match tag:
            case MoveTags.CHECK:
                update_pos_command = command_manager.get(command_manager.COMMANDS.UPDATE_FEN, self.fen.notation)
                ext_commands.append(update_pos_command)
            case MoveTags.CHECKMATE:
                end_game_command = command_manager.get(command_manager.COMMANDS.END_GAME)
                update_pos_command = command_manager.get(command_manager.COMMANDS.UPDATE_FEN, self.fen.notation)
                ext_commands.append(end_game_command)
                ext_commands.append(update_pos_command)
            case MoveTags.REGULAR:
                update_pos_command = command_manager.get(command_manager.COMMANDS.UPDATE_FEN, self.fen.notation)
                ext_commands.append(update_pos_command)
            case MoveTags.INVALID:
                invalid_move_command = command_manager.get(command_manager.COMMANDS.INVALID_MOVE)
                ext_commands.append(invalid_move_command)
            case MoveTags.TAKE:
                update_captured_pieces = command_manager.get(
                    command_manager.COMMANDS.UPDATE_CAP_PIECES,
                    self.captured_pieces
                )
                ext_commands.append(update_captured_pieces)
            case _:
                assert False, "INVALID MATCH.MOVE_TYPE"
        return ext_commands


def is_command_destination_valid(cmd_dest: str, is_white: bool) -> bool:
    if cmd_dest == chess_board.SIDE.WHITE.name and is_white: return True
    if cmd_dest == chess_board.SIDE.BLACK.name and not is_white: return True
    return False
