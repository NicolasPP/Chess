import queue, dataclasses

from config import *

@dataclasses.dataclass
class Command:
	info : str = ''

MATCH : queue.Queue[Command]= queue.Queue()
PLAYER : queue.Queue[Command]= queue.Queue()

EMPTY_Q : None  = None


def send_to( dest : queue.Queue, command : Command ) -> None: 
	dest.put( command )

def read_from(command_q : queue.Queue) -> Command | None:
	if command_q.empty(): return EMPTY_Q
	return command_q.get()


def move( from_coords : str, dest_coords : str, cmd_source : str ) -> Command:
	return Command(from_coords + C_SPLIT + dest_coords + C_SPLIT + cmd_source)

def update_pieces_pos() -> Command:
	return Command( PLAYER_COMMANDS.UPDATE_POS )

def next_turn() -> Command:
	return Command( PLAYER_COMMANDS.NEXT_TURN )