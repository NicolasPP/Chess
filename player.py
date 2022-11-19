import pygame
from dataclasses import dataclass
from enum import Enum
from config import *
import chess as CHESS

import asset as ASSETS



class STATE(Enum):
	IDLE 		: int = 0 # waiting your turn 
	PICK_PIECE 	: int = 1 #  picking a piece 
	DROP_PIECE 	: int = 2 # dropping the piece 

@dataclass
class Player:
	side   : CHESS.SIDE
	board  : CHESS.Board
	pieces : dict[str, CHESS.Piece]
	state  : STATE = STATE.IDLE



def PLAYER( *,
		side : CHESS.SIDE,
		piece_set : ASSETS.PIECE_SET,
		board_asset : ASSETS.BOARDS,
		scale : float,
	) -> Player:
	board = CHESS.get_board(board_asset.value, side, scale)
	pieces = CHESS.get_peices(piece_set.value, scale)
	player = Player( side, board, pieces )
	if side is CHESS.SIDE.WHITE: player.state = STATE.PICK_PIECE
	return player

def next_state( player : Player ) -> None:
	next_state = player.state.value + 1
	state_amount = len( list(STATE) )
	player.state = STATE( next_state % state_amount )