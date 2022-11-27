import socket

class Network:
	def __init__(self):
		self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server = '192.168.1.44'
		self.port = 5555
		self.address = (self.server, self.port)
		self.id = self.connect()

	def connect(self):
		try:
			self.client.connect(self.address)
			return self.read()
		except socket.error as e:
			print( f'error connecting : {e}')

	def send(self, data):
		try:
			self.client.send(str.encode(data))
			return self.read()
		except socket.error as e:
			print( f'error sending : {e}')

	def read(self):
		return self.client.recv(2048).decode()

