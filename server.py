import _thread as thread
import logging
import socket as SKT

import click

from chess import match as MATCH
from config import *
from utils import commands as CMD
from utils import network as NET

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
			move_type = server.match.process_move(move_info)
			logging.debug("move type : %s", move_type.name)
			
			match(move_type):
				case MATCH.MOVE_TYPE.CHECK:
					print(MATCH.MOVE_TYPE.CHECK)
					next_turn_command = I_SPLIT.join([CMD.get(CMD.COMMANDS.NEXT_TURN).info, NO_INFO])
					update_pos_command = I_SPLIT.join([CMD.get(CMD.COMMANDS.UPDATE_POS).info, server.match.fen.get_notation()])
					commands.append(next_turn_command)
					commands.append(update_pos_command)
				case MATCH.MOVE_TYPE.CHECKMATE:
					print(MATCH.MOVE_TYPE.CHECKMATE)
					update_pos_command = I_SPLIT.join([CMD.get(CMD.COMMANDS.UPDATE_POS).info, server.match.fen.get_notation()])
					commands.append(update_pos_command)
				case MATCH.MOVE_TYPE.CASTLE:
					assert False, "CASTLE Not implemented"
				case MATCH.MOVE_TYPE.EN_PASSANT:
					assert False, "EN_PASSANT Not implemented"
				case MATCH.MOVE_TYPE.REGULAR:
					next_turn_command = I_SPLIT.join([CMD.get(CMD.COMMANDS.NEXT_TURN).info, NO_INFO])
					update_pos_command = I_SPLIT.join([CMD.get(CMD.COMMANDS.UPDATE_POS).info, server.match.fen.get_notation()])
					commands.append(next_turn_command)
					commands.append(update_pos_command)
				case MATCH.MOVE_TYPE.INVALID:
					invalid_move_command = I_SPLIT.join([CMD.get(CMD.COMMANDS.INVALID_MOVE).info, NO_INFO])
					commands.append(invalid_move_command)
				case _:
					assert False, "INVALID MATCH.MOVE_TYPE"


			server.match.update_pos = True
			server.match.commands = commands
		server.client_sockets.remove(client_socket)
		logging.info("client : %s  disconnected", p_id)

@click.command()
@click.option('--ip', default = '127.0.0.1', help = 'set ip adress of server, default = 127.0.0.1')
def start_server(ip : str) -> None:
	Server(ip).run()

if __name__ == '__main__':
	start_server()