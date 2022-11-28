import socket as SKT
import _thread as thread
import network as NET
from config import *
from chess import match as MATCH
from chess import game as GAME


'''
[Errno 48] Address already in use
you can get the process ID with port with this command : sudo lsof -i:PORT
'''

class Server(NET.Net):
	def __init__(self):
		super().__init__()
		self.client_id : int = -1
		self.match : MATCH.Match = MATCH.MATCH()

	def start(self) -> None:
		try:
			self.socket.bind(self.address)
		except SKT.error as e:
			print( f'error binding : {e}')

		self.socket.listen()

		print("Waiting for a connection, Server Started")

	def run(self) -> None:
		self.start()
		while True:
			conn, addr = self.socket.accept()
			print("Connected to:", addr)
			thread.start_new_thread(threaded_client, (conn, self,))

	def get_id(self) -> str:
		self.client_id += 1
		return str(self.client_id)





def threaded_client(conn : SKT.socket, server : Server):
	conn_id = server.get_id()
	conn.send(str.encode(conn_id))
	while True:
		try:
			data = conn.recv(2048).decode("utf-8")
			if not data: break
			
			if data != NO_MOVE: 
				processed_move = MATCH.process_move( data, server.match )
				if processed_move: print( data )

			conn.send(str.encode(server.match.fen.notation))
		except:
			break

	print(f"Lost connection to id : {conn_id}")
	conn.close()


if __name__ == '__main__':
	Server().run()




