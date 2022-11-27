import socket as SKT
import _thread as thread
import network as NET



class Server(NET.Net):
	def __init__(self):
		super().__init__()
		self.client_id = -1

	def start(self):
		try:
			self.socket.bind(self.address)
		except SKT.error as e:
			print( f'error binding : {e}')

		self.socket.listen()

		print("Waiting for a connection, Server Started")

	def run(self):
		self.start()
		while True:
			conn, addr = self.socket.accept()
			print("Connected to:", addr)
			thread.start_new_thread(threaded_client, (conn, self))

	def get_id(self):
		self.client_id += 1
		return str(self.client_id)






def threaded_client(conn, server):
	conn.send(str.encode(server.get_id()))
	reply = ""
	while True:
		try:
			data = conn.recv(2048)
			reply = data.decode("utf-8")

			if not data:
				print("Disconnected")
				break
			else:
				print("Received: ", reply)

			conn.send(str.encode('its me'))
		except:
			break

	print("Lost connection")
	conn.close()


if __name__ == '__main__':
	Server().run()




