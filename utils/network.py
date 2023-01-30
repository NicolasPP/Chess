import socket as SKT

class Net:
	def __init__(self, server_ip):
		self.server = server_ip
		self.socket : SKT.socket = SKT.socket(SKT.AF_INET, SKT.SOCK_STREAM)
		self.port : int = 5555
		self.address : tuple[str, int]= (self.server, self.port)

class Network(Net):
	def __init__(self, server_ip : str):
		super().__init__(server_ip)
		self.id = int(self.connect())

	def connect(self) -> str:
		try:
			self.socket.connect(self.address)
			return self.read()
		except SKT.error as e:
			print( f'error connecting : {e}')
			return 'error'

	def read(self) -> str:
		return self.socket.recv(2048).decode()