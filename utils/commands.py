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
def get(command: COMMANDS, *args) -> Command:
    match command:
        case COMMANDS.UPDATE_POS:
            return get_update_pieces_pos()
        case COMMANDS.END_GAME:
            return get_end_game()
        case COMMANDS.INVALID_MOVE:
            return get_invalid_move()
        case COMMANDS.MOVE:
            return get_move(*args)
        case _:
            assert False, f" {command.name} : Command not recognised"


def get_move(from_coordinates: str, dest_coordinates: str, player_side: str, target_fen: str) -> Command:
    return Command(I_SPLIT.join([from_coordinates, dest_coordinates, player_side, target_fen]))


def get_update_pieces_pos() -> Command:
    return Command(COMMANDS.UPDATE_POS.value)


def get_end_game() -> Command:
    return Command(COMMANDS.END_GAME.value)


def get_invalid_move() -> Command:
    return Command(COMMANDS.INVALID_MOVE.value)
# ---------------------
