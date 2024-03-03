import socket


class Net:
    def __init__(self, server_ip):
        self.host = server_ip
        self.socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port: int = 3389
        self.address: tuple[str, int] = (self.host, self.port)

    def set_ip_address(self, server_ip: str) -> None:
        self.host = server_ip
        self.address = (self.host, self.port)

    def reset_socket(self) -> None:
        self.socket.close()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
