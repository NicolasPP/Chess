import socket as skt


class ServerUser:
    def __init__(self, socket: skt.socket, address: tuple[str, int]):
        self.socket: skt.socket = socket
        self.address: tuple[str, int] = address


