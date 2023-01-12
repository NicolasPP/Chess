import logging, click

import socket as SKT
import _thread as thread

from utils import network as NET
from utils import commands as CMD
from chess import match as MATCH

from config import *

'''
[Errno 48] Address already in use
you can get the process ID with port with this command : sudo lsof -i:PORT
'''


logging.basicConfig(
	filename='log/server.log',
	encoding='utf-8',
	level=logging.DEBUG,
	filemode='w',
	format='%(asctime)s\t%(levelname)s\t%(message)s'
)


class Server(NET.Net):
	def __init__(self, server_ip : str):
		super().__init__(server_ip)
		self.client_id : int = -1
		self.match : MATCH.Match = MATCH.Match()
		self.client_sockets : list[SKT.socket] = []

	def start(self) -> None:
		logging.info('Server started')
		print(f'server started at {self.server}')
		try:
			self.socket.setsockopt(SKT.SOL_SOCKET, SKT.SO_REUSEADDR, 1)
			self.socket.bind(self.address)
		except SKT.error as e:
			logging.debug("error binding : %s", e )

		self.socket.listen()

		logging.info("Waiting for clients to connect")

	def run(self) -> None:
		self.start()
		thread.start_new_thread(game_logic, (self,))
		while True:
			client_socket, addr = self.socket.accept()
			logging.info("Connected to address : %s", addr)


			self.client_sockets.append(client_socket)
			thread.start_new_thread(client_listener, (client_socket, self,))

	def get_id(self) -> str:
		self.client_id += 1
		return str(self.client_id)

	def send_all_clients(self, data : str):
		for client_socket in self.client_sockets:
			client_socket.send(str.encode(data))


def game_logic(server : Server):
	while True:
		if server.match.update_pos:
			server.match.commands.append(END_MARKER)
			server.send_all_clients(C_SPLIT.join(server.match.commands))
			server.match.update_pos = False
			server.match.commands = []

def client_listener(client_socket: SKT.socket, server : Server):
	with client_socket:
		p_id = server.get_id()
		client_socket.send(str.encode(p_id))
		while True:
			data : bytes = client_socket.recv(DATA_SIZE)
			if not data: break
			commands = []
			move_info = data.decode('utf-8')
			logging.debug("client : %s, sent move %s to server", p_id, move_info)
			if server.match.process_move(move_info):
				next_turn_command = I_SPLIT.join([CMD.get_next_turn().info, NO_INFO])
				update_pos_command = I_SPLIT.join([CMD.get_update_pieces_pos().info, server.match.fen.notation])
				commands.append(next_turn_command)
				commands.append(update_pos_command)
			else:
				invalid_move_command = I_SPLIT.join([CMD.get_invalid_move().info, NO_INFO])
				commands.append(invalid_move_command)

			server.match.update_pos = True
			server.match.commands = commands
		server.client_sockets.remove(client_socket)
		logging.info("client : %s  disconnected", p_id)

@click.command()
@click.option('--ip', default = '127.0.0.1')
def start_server(ip : str) -> None: 
	Server(ip).run()

if __name__ == '__main__': 
	start_server()