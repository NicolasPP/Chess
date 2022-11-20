from enum import Enum
from queue import Queue
from typing import TypeAlias
from dataclasses import dataclass


@dataclass
class Move:
	from_coords : str = ''
	dest_coords : str = ''

Command : TypeAlias = Move
COMMAND_Q : Queue[Command]= Queue()

def send_command( command : Command ) -> None: 
	COMMAND_Q.put( command )

def get_command(  ) -> Command | None:
	if COMMAND_Q.empty(): return None
	command = COMMAND_Q.get()
	return command



