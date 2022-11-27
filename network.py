import socket as SKT


class Net:
	def __init__(self):
		self.socket = SKT.socket(SKT.AF_INET, SKT.SOCK_STREAM)
		self.server = '192.168.1.44'
		self.port = 5555
		self.address = (self.server, self.port)

	
		

class Network(Net):
	def __init__(self):
		super().__init__()
		self.id = self.connect()

	def connect(self):
		try:
			self.socket.connect(self.address)
			return self.read()
		except SKT.error as e:
			print( f'error connecting : {e}')

	def send(self, data):
		try:
			self.socket.send(str.encode(data))
			return self.read()
		except SKT.error as e:
			print( f'error sending : {e}')

	def read(self):
		return self.socket.recv(2048).decode()

	

	

