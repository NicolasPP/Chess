import pygame, sys, random, logging

from random import choice

from utils import asset as ASSETS
from utils import debug as DB
from chess import chess_data as CHESS
from chess import player as PLAYER
from utils import FEN_notation as FENN
from utils import network as NET

import socket as SKT
import _thread as thread

from config import *

logging.basicConfig(
	filename='log/client.log',
	encoding='utf-8',
	level=logging.DEBUG,
	filemode='w',
	format='%(asctime)s\t%(levelname)s\t%(message)s'
)



pygame.init()
window_size = pygame.math.Vector2(WINDOW_SIZE)
pygame.display.set_mode(window_size)
done = False
clock = pygame.time.Clock()
network = NET.Network()


def server_listener(player : PLAYER.Player, server_socket : SKT.socket, match_fen : FENN.Fen) -> None:
	with server_socket:
		prev_data_tail = ''
		while True:
			data : bytes = server_socket.recv(DATA_SIZE)
			if not data: break
			prev_data_tail = ''
			data, prev_data_tail = correct_data(data.decode('utf-8'), prev_data_tail)
			for command_info in data[:-1].split(INFO_SPLIT):
				command, info = command_info.split(C_SPLIT)
				logging.debug("recieved %s from server", command)
				logging.debug("command info : \n%s", info)
				if command == PLAYER_COMMANDS.UPDATE_POS:
					match_fen.notation = info
					PLAYER.update_pieces_location(player, match_fen)
				elif command == PLAYER_COMMANDS.NEXT_TURN:
					PLAYER.next_turn(player)
		logging.debug("server disconnected")


def correct_data(received_data : str, prev_data_tail : str) -> tuple[str,str]:
	last_char = received_data[-1]
	temp_data = received_data.split(END_MARKER)

	if temp_data[-1] == '': temp_data = temp_data[:-1]

	if last_char != END_MARKER:
		prev_data_tail = temp_data[-1]
		temp_data = temp_data[:-1]
		logging.debug("Data is incomplete, Tail : %s", prev_data_tail)
		logging.debug("Last correct pair : %s", temp_data[-1])
	return temp_data[-1], prev_data_tail


def update_window_caption(player: PLAYER.Player) -> None:
	if player.turn: pygame.display.set_caption(f"{player.side.name}s TURN")
	else:
		if player.side == CHESS.SIDE.WHITE:
			pygame.display.set_caption(f"BLACKs TURN")
		elif player.side == CHESS.SIDE.BLACK:
			pygame.display.set_caption(f"WHITEs TURN")
 	

white_player = PLAYER.PLAYER(
		side =CHESS.SIDE.WHITE,
		piece_set = random.choice(list(ASSETS.PIECE_SET)),
		board_asset = random.choice(list(ASSETS.BOARDS)),
		scale = BOARD_SCALE
	)

black_player = PLAYER.PLAYER(
		side = CHESS.SIDE.BLACK,
		piece_set = random.choice(list(ASSETS.PIECE_SET)),
		board_asset = random.choice(list(ASSETS.BOARDS)),
		scale = BOARD_SCALE
	)


player = white_player if network.id % 2 == 0 else black_player

# placing boards in the middle of the screen
screen_center = window_size / 2
player.board.pos_rect.center = round(screen_center.x), round(screen_center.y)


bg_color = 'white' if player.side == CHESS.SIDE.WHITE else 'black'
font_color = 'black' if player.side == CHESS.SIDE.WHITE else 'white'


match_fen = FENN.Fen()

thread.start_new_thread(server_listener, (player, network.socket, match_fen))
PLAYER.update_pieces_location(player, match_fen)
while not done:
	
	fps = round(clock.get_fps())
	pygame.display.get_surface().fill(bg_color)


	for event in pygame.event.get():
		if event.type == pygame.QUIT: done = True
		PLAYER.parse_player_input( event, player, match_fen, network )

	update_window_caption(player)
	PLAYER.render_board( player )
	PLAYER.render_pieces( player )

	DB.debug(fps, font_color)
	pygame.display.flip()
	clock.tick()

pygame.quit()
sys.exit()