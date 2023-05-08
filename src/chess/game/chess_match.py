import datetime
import enum

from chess.timer.timer_config import TimerConfig
from chess.board.side import Side
from chess.notation.algebraic_notation import AlgebraicNotation
from chess.network.command_manager import Command, CommandManager, ClientCommand, ServerCommand
from chess.notation.forsyth_edwards_notation import encode_fen_data, Fen, FenChars, validate_fen_piece_placement
from chess.notation.forsyth_edwards_notation import validate_fen_castling_rights, validate_fen_en_passant_rights
from chess.movement.validate_move import is_move_valid, is_take, is_check
from chess.movement.validate_move import is_checkmate, is_stale_mate, is_material_insufficient

from config.pg_config import HALF_MOVE_LIMIT


class MoveTags(enum.Enum):
    CHECK = enum.auto()
    CHECKMATE = enum.auto()
    REGULAR = enum.auto()
    INVALID = enum.auto()
    TAKE = enum.auto()


class MatchResult(enum.Enum):
    WHITE = enum.auto()
    BLACK = enum.auto()
    DRAW = enum.auto()


class MatchResultType(enum.Enum):
    CHECKMATE = enum.auto()
    RESIGNATION = enum.auto()
    TIMEOUT = enum.auto()
    AGREEMENT = enum.auto()
    STALEMATE = enum.auto()
    INSUFFICIENT_MATERIAL = enum.auto()
    FIFTY_MOVE_RULE = enum.auto()
    REPETITION = enum.auto()


class RepetitionCounter:
    def __init__(self) -> None:
        self.reached_positions: dict[str, int] = {}
        self.three_fold_repetition: bool = False

    def add_position(self, piece_placement: str, en_passant: str, castling_rights: str) -> None:
        validate_fen_piece_placement(piece_placement)
        validate_fen_en_passant_rights(en_passant)
        validate_fen_castling_rights(castling_rights)
        position = piece_placement + en_passant + castling_rights
        if position not in self.reached_positions:
            self.reached_positions[position] = 1
            return

        if self.reached_positions[position] >= 2:
            self.three_fold_repetition = True
        else:
            self.reached_positions[position] += 1

    def is_three_fold_repetition(self) -> bool: return self.three_fold_repetition


class Match:
    def __init__(self, timer_config: TimerConfig):
        self.fen: Fen = Fen()
        self.captured_pieces: str = ''
        self.commands: list[Command] = []
        self.update_fen: bool = False
        self.timer_config = timer_config
        self.prev_time: datetime.datetime | None = None
        self.white_time_left: float = timer_config.time
        self.black_time_left: float = timer_config.time
        self.repetition_counter: RepetitionCounter = RepetitionCounter()

    def process_client_command(self, command: Command, commands: list[Command]) -> list[Command]:
        end_game_info: dict[str, str] = {}
        move_tags: list[MoveTags] = []
        before_move_fen: Fen = Fen(encode_fen_data(self.fen.data))
        if command.name == ClientCommand.PICKING_PROMOTION.name:
            commands.append(CommandManager.get(ServerCommand.CLIENT_PROMOTING))

        elif command.name == ClientCommand.MOVE.name:
            move_tags = self.process_move(command, before_move_fen)

        elif command.name == ClientCommand.RESIGN.name:
            side = command.info[CommandManager.side]
            result = MatchResult.BLACK.name if side == Side.WHITE.name else MatchResult.WHITE.name
            end_game_info[CommandManager.game_result_type] = MatchResultType.RESIGNATION.name
            end_game_info[CommandManager.game_result] = result
            commands.append(CommandManager.get(ServerCommand.END_GAME, end_game_info))

        elif command.name == ClientCommand.OFFER_DRAW.name:
            commands.append(CommandManager.get(ServerCommand.CLIENT_DRAW_OFFER, command.info))

        elif command.name == ClientCommand.DRAW_RESPONSE.name:
            if bool(int(command.info[CommandManager.draw_offer_result])):
                end_game_info[CommandManager.game_result_type] = MatchResultType.AGREEMENT.name
                end_game_info[CommandManager.game_result] = MatchResult.DRAW.name
                commands.append(CommandManager.get(ServerCommand.END_GAME, end_game_info))
            else:
                commands.append(CommandManager.get(ServerCommand.CONTINUE))

        elif command.name == ClientCommand.TIME_OUT.name:
            side = command.info[CommandManager.side]
            result = MatchResult.BLACK.name if side == Side.WHITE.name else MatchResult.WHITE.name
            end_game_info[CommandManager.game_result_type] = MatchResultType.TIMEOUT.name
            end_game_info[CommandManager.game_result] = result
            commands.append(CommandManager.get(ServerCommand.END_GAME, end_game_info))

        else:
            assert False, f" {command.name} : Command not recognised"

        if command.name == ClientCommand.MOVE.name:
            from_index = AlgebraicNotation.get_index_from_an(*command.info[CommandManager.from_coordinates])
            dest_index = AlgebraicNotation.get_index_from_an(*command.info[CommandManager.dest_coordinates])

            for tag in move_tags:
                commands.extend(self.process_tag(tag, from_index, dest_index))

        commands.extend(self.process_match_state(commands))

        return commands

    def process_local_move(self) -> None:
        command: Command | None = CommandManager.read_from(CommandManager.MATCH)
        if command is None: return
        commands: list[Command] = []
        commands = self.process_client_command(command, commands)

        list(map(lambda cmd: CommandManager.send_to(CommandManager.PLAYER, cmd), commands))

    def process_move(self, command: Command, before_move_fen: Fen) -> list[MoveTags]:
        from_index = AlgebraicNotation.get_index_from_an(*command.info[CommandManager.from_coordinates])
        dest_index = AlgebraicNotation.get_index_from_an(*command.info[CommandManager.dest_coordinates])
        side = command.info[CommandManager.side]
        target_fen = command.info[CommandManager.target_fen]
        time_iso = command.info[CommandManager.time_iso]

        if not is_side_valid(side, self.fen.is_white_turn()) \
                or not is_move_valid(from_index, dest_index, self.fen):
            return [MoveTags.INVALID]

        time = datetime.datetime.fromisoformat(time_iso)
        if self.prev_time is not None:
            diff = time - self.prev_time
            if self.fen.data.active_color == FenChars.WHITE_ACTIVE_COLOR:
                self.white_time_left -= diff.total_seconds()
                self.white_time_left += self.timer_config.increment
            else:
                self.black_time_left -= diff.total_seconds()
                self.black_time_left += self.timer_config.increment

        self.prev_time = time
        self.fen.make_move(from_index, dest_index, target_fen)
        self.repetition_counter.add_position(
            self.fen.data.piece_placement,
            self.fen.data.en_passant_rights,
            self.fen.data.castling_rights
        )
        return self.get_move_tags(before_move_fen, from_index, dest_index)

    def get_move_tags(self, before_move_fen: Fen, from_index: int, dest_index: int) -> list[MoveTags]:
        tags = []

        is_en_passant = before_move_fen.is_move_en_passant(from_index, dest_index)
        is_castle = before_move_fen.is_move_castle(from_index, dest_index)
        opponent_pawn_fen = FenChars.get_piece_fen(FenChars.DEFAULT_PAWN, not before_move_fen.is_white_turn())

        if is_take(before_move_fen, dest_index, is_en_passant, is_castle):
            if is_en_passant:
                self.captured_pieces += opponent_pawn_fen
            else:
                self.captured_pieces += before_move_fen[dest_index]
            tags.append(MoveTags.TAKE)

        if is_checkmate(self.fen, self.fen.is_white_turn()):
            tags.append(MoveTags.CHECKMATE)
        elif is_check(self.fen, self.fen.is_white_turn()):
            tags.append(MoveTags.CHECK)
        else:
            tags.append(MoveTags.REGULAR)

        return tags

    def process_tag(self, tag: MoveTags, from_index: int, dest_index: int) -> list[Command]:
        ext_commands = []
        update_fen_info: dict[str, str] = {
            CommandManager.fen_notation: self.fen.notation,
            CommandManager.white_time_left: str(self.white_time_left),
            CommandManager.black_time_left: str(self.black_time_left),
            CommandManager.from_index: str(from_index),
            CommandManager.dest_index: str(dest_index)
        }
        update_fen_command: Command = CommandManager.get(ServerCommand.UPDATE_FEN, update_fen_info)
        if tag == MoveTags.CHECK:
            ext_commands.append(update_fen_command)
        elif tag == MoveTags.CHECKMATE:
            result = MatchResult.BLACK.name if self.fen.is_white_turn() else MatchResult.WHITE.name
            end_game_info: dict[str, str] = {
                CommandManager.game_result_type: MatchResultType.CHECKMATE.name,
                CommandManager.game_result: result
            }
            end_game_command: Command = CommandManager.get(ServerCommand.END_GAME, end_game_info)
            ext_commands.append(update_fen_command)
            ext_commands.append(end_game_command)
        elif tag == MoveTags.REGULAR:
            ext_commands.append(update_fen_command)
        elif tag == MoveTags.INVALID:
            invalid_move_command: Command = CommandManager.get(ServerCommand.INVALID_MOVE)
            ext_commands.append(invalid_move_command)
        elif tag == MoveTags.TAKE:
            update_captured_info: dict[str, str] = {CommandManager.captured_pieces: self.captured_pieces}
            update_captured_pieces = CommandManager.get(ServerCommand.UPDATE_CAP_PIECES, update_captured_info)
            ext_commands.append(update_captured_pieces)
        else:
            assert False, "INVALID MATCH.MOVE_TAG"
        return ext_commands

    def process_match_state(self, commands: list[Command]) -> list[Command]:
        # -- WIN / LOOSE --

        # Checkmate
        for command in commands:
            if command.name == ServerCommand.END_GAME.name: return []

        # -- DRAW --
        # Stalemate
        draw_info: dict[str, str] = {CommandManager.game_result: MatchResult.DRAW.name}

        if is_stale_mate(self.fen):
            draw_info[CommandManager.game_result_type] = MatchResultType.STALEMATE.name
            return [CommandManager.get(ServerCommand.END_GAME, draw_info)]

        # Insufficient Material
        if is_material_insufficient(self.fen):
            draw_info[CommandManager.game_result_type] = MatchResultType.INSUFFICIENT_MATERIAL.name
            return [CommandManager.get(ServerCommand.END_GAME, draw_info)]

        # 50 move-rule
        if int(self.fen.data.half_move_clock) >= HALF_MOVE_LIMIT:
            draw_info[CommandManager.game_result_type] = MatchResultType.FIFTY_MOVE_RULE.name
            return [CommandManager.get(ServerCommand.END_GAME, draw_info)]

        # Repetition
        if self.repetition_counter.is_three_fold_repetition():
            draw_info[CommandManager.game_result_type] = MatchResultType.REPETITION.name
            return [CommandManager.get(ServerCommand.END_GAME, draw_info)]

        return []


def is_side_valid(side: str, is_white: bool) -> bool:
    if side == Side.WHITE.name and is_white: return True
    if side == Side.BLACK.name and not is_white: return True
    return False
