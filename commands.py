from queue import Queue
from dataclasses import dataclass
from config import *

@dataclass
class Command:
	info : str = ''

MATCH : Queue[Command]= Queue()
PLAYER : Queue[Command]= Queue()

EMPTY_Q : None  = None


def send_to( dest : Queue, command : Command ) -> None: 
	dest.put( command )

def read_from(command_q : Queue) -> Command | None:
	if command_q.empty(): return EMPTY_Q
	return command_q.get()


def move( from_coords : str, dest_coords : str, cmd_source : str ) -> Command:
	return Command(from_coords + C_SPLIT + dest_coords + C_SPLIT + cmd_source)

def update_pieces_pos() -> Command:
	return Command( PLAYER_COMMANDS.UPDATE_POS )

def next_turn() -> Command:
	return Command( PLAYER_COMMANDS.NEXT_TURN )