import socket as skt


class Net:
    def __init__(self, server_ip):
        self.host = server_ip
        self.socket: skt.socket = skt.socket(skt.AF_INET, skt.SOCK_STREAM)
        self.port: int = 3389
        self.address: tuple[str, int] = (self.host, self.port)


class Network(Net):
    def __init__(self, server_ip: str):
        super().__init__(server_ip)
        self.id = int(self.connect())

    def connect(self) -> str:
        try:
            self.socket.connect(self.address)
            return self.read()
        except skt.error as e:
            print(f'error connecting : {e}')
            return 'error'

    def read(self) -> str:
        return self.socket.recv(2048).decode()
