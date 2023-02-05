import dataclasses
import enum
import queue

from config import *


class COMMANDS(enum.Enum):
    UPDATE_POS: str = 'update_pos'
    END_GAME: str = 'end_game'
    MOVE: str = 'move'
    INVALID_MOVE: str = 'invalid_move'


# -- Data --
@dataclasses.dataclass
class Command:
    info: str = ''


MATCH: queue.Queue[Command] = queue.Queue()
PLAYER: queue.Queue[Command] = queue.Queue()


# ----------

# -- Read and Write to Q -- 
def send_to(dest: queue.Queue, command: Command) -> None:
    dest.put(command)


def read_from(command_q: queue.Queue) -> Command | None:
    if command_q.empty(): return EMPTY_Q
    return command_q.get()


# -------------------------

# -- Command Getters --
def get(command: COMMANDS, from_coordinates: str = '', dest_coordinates: str = '', player_side: str = '') -> Command:
    match command:
        case COMMANDS.UPDATE_POS:
            return get_update_pieces_pos()
        case COMMANDS.END_GAME:
            return get_end_game()
        case COMMANDS.INVALID_MOVE:
            return get_invalid_move()
        case COMMANDS.MOVE:
            assert from_coordinates != '', 'invalid coordinates for picked piece'
            assert dest_coordinates != '', 'invalid coordinates for destination piece'
            assert player_side != '', 'invalid player side'
            return get_move(from_coordinates, dest_coordinates, player_side)
        case _:
            assert False, f" {command.name} : Command not recognised"


def get_move(from_coordinates: str, dest_coordinates: str, player_side: str) -> Command:
    return Command(from_coordinates + I_SPLIT + dest_coordinates + I_SPLIT + player_side)


def get_update_pieces_pos() -> Command:
    return Command(COMMANDS.UPDATE_POS.value)


def get_end_game() -> Command:
    return Command(COMMANDS.END_GAME.value)


def get_invalid_move() -> Command:
    return Command(COMMANDS.INVALID_MOVE.value)
# ---------------------
