import enum
import datetime

import chess.board as chess_board
import chess.validate_move as validate_move

from utils.algebraic_notation import get_index_from_an
from utils.forsyth_edwards_notation import encode_fen_data, Fen, FenChars
from chess.chess_timer import TimerConfig
from utils.command_manager import Command, CommandManager, Type
from config import *


class MoveTags(enum.Enum):
    CHECK = enum.auto()
    CHECKMATE = enum.auto()
    REGULAR = enum.auto()
    INVALID = enum.auto()
    TAKE = enum.auto()


class Match:
    def __init__(self, timer_config: TimerConfig):
        self.fen: Fen = Fen()
        self.moves: list[str] = []
        self.captured_pieces: str = ''
        self.commands: list[Command] = []
        self.update_fen: bool = False
        self.timer_config = timer_config
        self.prev_time: datetime.datetime | None = None
        self.white_time_left: float = timer_config.time
        self.black_time_left: float = timer_config.time

    # def process_local_move(self) -> None:
    #     command = command_manager.read_from(command_manager.MATCH)
    #     if command is None: return
    #     move_tags = self.process_move(command.info)
    #
    #     commands = []
    #
    #     for tag in move_tags:
    #         commands.extend(self.process_tag(tag))
    #
    #     commands.extend(self.process_match_state(commands))
    #
    #     list(map(lambda cmd: command_manager.send_to(command_manager.PLAYER, cmd), commands))

    def process_move(self, command: Command) -> list[MoveTags]:
        # fc, dc, cmd_dest, target_fen, move_time = command_info.split(I_SPLIT)
        from_index = get_index_from_an(*command.info['from_coordinates'])
        dest_index = get_index_from_an(*command.info['dest_coordinates'])
        side = command.info['side']
        target_fen = command.info['target_fen']
        move_time = command.info['time_iso']
        # from_index, dest_index = get_index_from_an(*fc), get_index_from_an(*dc)
        before_move_fen = Fen(encode_fen_data(self.fen.data))

        if not is_side_valid(side, self.fen.is_white_turn()) \
                or not validate_move.is_move_valid(from_index, dest_index, self.fen):
            return [MoveTags.INVALID]

        time = datetime.datetime.fromisoformat(move_time)
        if self.prev_time is not None:
            diff = time - self.prev_time
            if self.fen.data.active_color == FenChars.WHITE_ACTIVE_COLOR.value:
                self.white_time_left -= diff.total_seconds()
                self.white_time_left += self.timer_config.increment
            else:
                self.black_time_left -= diff.total_seconds()
                self.black_time_left += self.timer_config.increment

        self.prev_time = time
        self.fen.make_move(from_index, dest_index, target_fen)
        # self.moves.append(command_info)
        return self.get_move_tags(before_move_fen, from_index, dest_index)

    def get_move_tags(self, before_move_fen: Fen, from_index: int, dest_index: int) -> list[MoveTags]:
        tags = []

        is_en_passant = before_move_fen.is_move_en_passant(from_index, dest_index)
        is_castle = before_move_fen.is_move_castle(from_index, dest_index)
        opponent_pawn_fen = FenChars.DEFAULT_PAWN.get_piece_fen(not before_move_fen.is_white_turn())

        if validate_move.is_take(before_move_fen, dest_index, is_en_passant, is_castle):
            if is_en_passant:
                self.captured_pieces += opponent_pawn_fen
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

    def process_tag(self, tag: MoveTags) -> list[Command]:
        ext_commands = []
        match tag:
            case MoveTags.CHECK:
                update_fen_command = CommandManager.get(
                    Type.UPDATE_FEN,
                    fen_notation=self.fen.notation,
                    white_time_left=self.white_time_left,
                    black_time_left=self.black_time_left
                )
                ext_commands.append(update_fen_command)
            case MoveTags.CHECKMATE:
                end_game_command = CommandManager.get(Type.END_GAME)
                update_fen_command = CommandManager.get(
                    Type.UPDATE_FEN,
                    fen_notation=self.fen.notation,
                    white_time_left=self.white_time_left,
                    black_time_left=self.black_time_left
                )
                ext_commands.append(end_game_command)
                ext_commands.append(update_fen_command)
            case MoveTags.REGULAR:
                update_fen_command = CommandManager.get(
                    Type.UPDATE_FEN,
                    fen_notation=self.fen.notation,
                    white_time_left=self.white_time_left,
                    black_time_left=self.black_time_left
                )
                ext_commands.append(update_fen_command)
            case MoveTags.INVALID:
                invalid_move_command = CommandManager.get(Type.INVALID_MOVE)
                ext_commands.append(invalid_move_command)
            case MoveTags.TAKE:
                update_captured_pieces = CommandManager.get(
                    Type.UPDATE_CAP_PIECES,
                    captured_pieces=self.captured_pieces
                )
                ext_commands.append(update_captured_pieces)
            case _:
                assert False, "INVALID MATCH.MOVE_TAG"
        return ext_commands

    def process_match_state(self, commands: list[Command]) -> list[Command]:
        # -- WIN / LOOSE --

        # Checkmate
        for command in commands:
            if command.name == Type.END_GAME.name: return []

        # Resignation
        # Timeout
        if self.white_time_left <= 0 or self.black_time_left <= 0:
            return [CommandManager.get(Type.END_GAME)]

        # -- DRAW --
        # Stalemate
        # Insufficient Material
        if self.fen.is_material_insufficient():
            return [CommandManager.get(Type.END_GAME)]

        # 50 move-rule
        if int(self.fen.data.half_move_clock) >= HALF_MOVE_LIMIT:
            return [CommandManager.get(Type.END_GAME)]

        # Repetition
        # Agreement

        return []


def is_side_valid(side: str, is_white: bool) -> bool:
    if side == chess_board.SIDE.WHITE.name and is_white: return True
    if side == chess_board.SIDE.BLACK.name and not is_white: return True
    return False
