import socket as SKT



class Net:
	def __init__(self):
		self.socket : SKT.socket = SKT.socket(SKT.AF_INET, SKT.SOCK_STREAM)
		self.server : str = '192.168.1.44'
		self.port : int = 5555
		self.address : tuple[str, int]= (self.server, self.port)
		

class Network(Net):
	def __init__(self):
		super().__init__()
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

