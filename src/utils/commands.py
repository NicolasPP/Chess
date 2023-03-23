import dataclasses
import enum
import queue

from config import *


class COMMANDS(enum.Enum):
    UPDATE_FEN: str = 'update_fen'
    END_GAME: str = 'end_game'
    MOVE: str = 'move'
    INVALID_MOVE: str = 'invalid_move'
    UPDATE_CAP_PIECES: str = 'update_cap_pieces'


@dataclasses.dataclass
class Command:
    info: str = ''


MATCH: queue.Queue[Command] = queue.Queue()
PLAYER: queue.Queue[Command] = queue.Queue()


def send_to(dest: queue.Queue, command: Command) -> None:
    dest.put(command)


def read_from(command_q: queue.Queue) -> Command | None:
    if command_q.empty(): return EMPTY_Q
    return command_q.get()


def get(command: COMMANDS, *args) -> Command:
    match command:
        case COMMANDS.UPDATE_FEN:
            return get_update_fen(*args)
        case COMMANDS.END_GAME:
            return get_end_game()
        case COMMANDS.INVALID_MOVE:
            return get_invalid_move()
        case COMMANDS.MOVE:
            return get_move(*args)
        case COMMANDS.UPDATE_CAP_PIECES:
            return get_update_captured_pieces(*args)
        case _:
            assert False, f" {command.name} : Command not recognised"


def split_command_info(command_info: str) -> list[str]:
    return command_info.split(I_SPLIT, 1)


def get_move(
        from_coordinates: str,
        dest_coordinates: str,
        player_side: str,
        target_fen: str,
        move_time_iso: str
) -> Command:
    return Command(I_SPLIT.join([from_coordinates, dest_coordinates, player_side, target_fen, move_time_iso]))


def get_update_fen(fen_notation: str, white_time_left: float, black_time_left: float) -> Command:
    return Command(I_SPLIT.join([COMMANDS.UPDATE_FEN.value, fen_notation, str(white_time_left), str(black_time_left)]))


def get_end_game() -> Command:
    return Command(I_SPLIT.join([COMMANDS.END_GAME.value, NO_INFO]))


def get_invalid_move() -> Command:
    return Command(I_SPLIT.join([COMMANDS.INVALID_MOVE.value, NO_INFO]))


def get_update_captured_pieces(captured_pieces: str) -> Command:
    return Command(I_SPLIT.join([COMMANDS.UPDATE_CAP_PIECES.value, captured_pieces]))
