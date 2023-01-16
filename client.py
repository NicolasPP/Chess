import pygame, sys, random, logging, click

import socket as SKT
import _thread as thread

from chess import game as GAME
from chess import player as PLAYER
from chess import chess_data as CHESS
from utils import asset as ASSETS
from utils import FEN_notation as FENN
from utils import network as NET
from utils import debug as DB

from config import *

logging.basicConfig(
	filename='log/client.log',
	encoding='utf-8',
	level=logging.DEBUG,
	filemode='w',
	format='%(asctime)s\t%(levelname)s\t%(message)s'
)


def server_listener(player : PLAYER.Player, server_socket : SKT.socket, match_fen : FENN.Fen) -> None:
	with server_socket:
		prev_data_tail = ''
		while True:
			data_b : bytes = server_socket.recv(DATA_SIZE)
			if not data_b: break
			prev_data_tail = ''
			data, prev_data_tail = correct_data(data_b.decode('utf-8'), prev_data_tail)
			for command_info in data[:-1].split(C_SPLIT):
				command, info = command_info.split(I_SPLIT)
				logging.debug("recieved %s from server", command)
				logging.debug("command info : \n%s", info)
				player.parse_command(command, info, match_fen)
				
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
 	
def get_player(network: SKT.socket) -> PLAYER.Player:
	side = CHESS.SIDE.WHITE if network.id % 2 == 0 else CHESS.SIDE.BLACK
	player = PLAYER.Player(
		side =side,
		piece_set = random.choice(list(ASSETS.PIECE_SET)),
		board_asset = random.choice(list(ASSETS.BOARDS)),
		scale = BOARD_SCALE)
	return player

def center_board( player : PLAYER.Player, window_size : pygame.math.Vector2) -> None:
	screen_center = window_size / 2
	player.board.pos_rect.center = round(screen_center.x), round(screen_center.y)

def get_colors(player : PLAYER.Player) -> tuple[str, str]:
	bg_color = 'white' if player.side == CHESS.SIDE.WHITE else 'black'
	font_color = 'black' if player.side == CHESS.SIDE.WHITE else 'white'
	return bg_color, font_color

def run_main_loop(server_ip : str) -> None:
	pygame.init()
	window_size = pygame.math.Vector2(WINDOW_SIZE)
	pygame.display.set_mode(window_size)
	done = False
	clock = pygame.time.Clock()
	network = NET.Network(server_ip)
	match_fen = FENN.Fen()

	player = get_player(network)
	center_board(player, window_size)
	bg_color, font_color = get_colors(player)

	thread.start_new_thread(server_listener, (player, network.socket, match_fen))
	player.update_pieces_location(match_fen)
	while not done:
		
		fps = round(clock.get_fps())
	
		for event in pygame.event.get():
			if event.type == pygame.QUIT: done = True
			player.parse_input(event, match_fen, network = network)
	
		update_window_caption(player)
		player.render(bg_color)
	
		DB.debug(fps, bg_color, font_color)
		pygame.display.flip()
		clock.tick()
	
	pygame.quit()
	sys.exit()

@click.command()
@click.option('--server_ip', default = '127.0.0.1')
def start_client(server_ip : str) -> None:
	run_main_loop(server_ip)


if __name__ == '__main__':
	start_client()
