import pygame, enum, typing

from utils import asset as ASSETS
from utils import commands as CMD
from utils import FEN_notation as FENN
from utils import network as NET
from chess import chess_data as CHESS

from config import *




# -- Enums --
class MOUSECLICK(enum.Enum):
	LEFT 		: int = 1
	MIDDLE 		: int = 2
	RIGHT 		: int = 3
	SCROLL_UP 	: int = 4
	SCROLL_DOWN : int = 5

class STATE(enum.Enum):
	PICK_PIECE 	: int = 0 #  picking a piece 
	DROP_PIECE 	: int = 1 # dropping the piece 
# -----------




class Player:
	def __init__(self,
		side 		: CHESS.SIDE,
		piece_set 	: ASSETS.PIECE_SET,
		board_asset : ASSETS.BOARDS,
		scale 		: float):
		self.side 		: CHESS.SIDE 		= side
		self.board 		: CHESS.Board 		= CHESS.get_board(board_asset.value, side, scale)
		self.pieces  	: dict[str,  Piece] = CHESS.get_peices(piece_set.value, scale)
		self.turn 		: bool 				= side is CHESS.SIDE.WHITE
		self.state 		: STATE 			= STATE.PICK_PIECE


	# -- reading playing input --
	def parse_input(
		self,
		event : pygame.event.Event, 
		fen : FENN.Fen,
		network : NET.Network | None = None,
	 	local : bool = False) -> None:
		if event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == MOUSECLICK.LEFT.value: self.handle_mouse_down_left(fen)
		if event.type == pygame.MOUSEBUTTONUP:
			if event.button == MOUSECLICK.LEFT.value: self.hanle_left_mouse_up(network, fen, local)

	def hanle_left_mouse_up(self, network : NET.Network | None, fen : FENN.Fen, local : bool) -> None:
		if self.state is not STATE.DROP_PIECE: return
		board_square = CHESS.get_collided_board_square(self.board)
		if not board_square: return None
		
		CHESS.reset_board_grid(self.board)
		from_coords = CHESS.get_picked_up(self.board).AN_coordinates
		dest_coords = board_square.AN_coordinates
		move = CMD.get_move(from_coords, dest_coords, self.side.name)
		
		if local: CMD.send_to(CMD.MATCH, move)
		else: network.socket.send(str.encode(move.info))

		self.progress_state()
		CHESS.reset_picked_up(self.board)

	def handle_mouse_down_left(self, fen : FENN.Fen) -> None:
		board_square = CHESS.get_collided_board_square(self.board)
		if not board_square: return None
		if self.state is not STATE.PICK_PIECE: return
		if board_square.FEN_val is FEN.BLANK_PIECE: return 
		
		CHESS.set_picked_up(board_square, self.board, fen, self.side)
		self.progress_state()
	# ---------------------------


	# -- rendering players game --
	# TODO : Only rerender pieces which have changed place, maybe create a prev_fen member
	def render_board( self) -> None:
		pygame.display.get_surface().blit(self.board.sprite.surface, self.board.pos_rect)
		if self.state is STATE.DROP_PIECE: self.show_available_moves()

	def render_pieces(self) -> None:
		grid = self.board.grid if self.side is CHESS.SIDE.WHITE else self.board.grid[::-1]
		board_offset = pygame.math.Vector2(self.board.pos_rect.topleft)
		for board_square in grid:
			if board_square.FEN_val is FEN.BLANK_PIECE: continue
			pygame.display.get_surface().blit(
				board_square.piece_surface,
				CHESS.get_piece_render_pos(board_square, board_offset))

	def show_available_moves(self) -> None:
		picked = CHESS.get_picked_up(self.board)
		if not self.turn: return
		if self.side is CHESS.SIDE.WHITE:
			if picked.FEN_val.islower(): return
		if self.side is CHESS.SIDE.BLACK:
			if picked.FEN_val.isupper(): return
		board_offset = pygame.math.Vector2(self.board.pos_rect.topleft)
		for surface, pos in CHESS.get_available_moves_surface(picked, self.board):
			pygame.display.get_surface().blit(surface, pos)
	
	def update_pieces_location(self, fen : FENN.Fen) -> None:
		CHESS.reset_board_grid(self.board)
		for piece, board_square in self.fen_to_piece_board_square(fen):
			board_square.FEN_val = piece.FEN_val
			board_square.piece_surface = piece.sprite.surface

	def fen_to_piece_board_square(self, fen : FENN.Fen)\
	-> typing.Generator[tuple[CHESS.Piece, CHESS.Board_Square], None, None]:
		count = 0
		for piece_fen in FENN.iterate_FEN(fen):
			if piece_fen.isnumeric(): count += int( piece_fen ) -1
			else: yield self.pieces[piece_fen], self.board.grid[count]
			count += 1
	# ----------------------------

	def progress_state(self) -> None: self.state = STATE((self.state.value + 1) % len(list(STATE)))

	def swap_turn(self) -> None: self.turn = not self.turn


# -- Local Logic --
def exec_player_command(white_player : Player, black_player : Player, fen: FENN.Fen) -> None:
	command = CMD.read_from(CMD.PLAYER)
	if command is None: return
	if command.info == PLAYER_COMMANDS.UPDATE_POS:
		white_player.update_pieces_location(fen)
		black_player.update_pieces_location(fen)
	elif command.info == PLAYER_COMMANDS.NEXT_TURN:
		white_player.swap_turn()
		black_player.swap_turn()
		assert not (white_player.turn and black_player.turn)
# -----------------

