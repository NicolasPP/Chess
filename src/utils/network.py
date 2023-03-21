import socket as skt
import typing
from utils.forsyth_edwards_notation import FenData, validate_fen_data

from config import *


class ClientInitInfo(typing.NamedTuple):
    client_id: str
    fen_str: str
    time_left: str


class Net:
    def __init__(self, server_ip):
        self.host = server_ip
        self.socket: skt.socket = skt.socket(skt.AF_INET, skt.SOCK_STREAM)
        self.port: int = 3389
        self.address: tuple[str, int] = (self.host, self.port)


class ChessNetwork(Net):
    def __init__(self, server_ip: str):
        super().__init__(server_ip)
        self.id: int = -1

    def connect(self) -> ClientInitInfo | None:
        try:
            self.socket.connect(self.address)
        except skt.error as e:
            print(f'error connecting : {e}')
            return None
        init_data = self.read().split(C_SPLIT)
        if not is_init_data_valid(init_data):
            raise Exception("initial data corrupted, try connecting again")
        self.id = int(init_data[0])
        return ClientInitInfo(*init_data)

    def read(self) -> str:
        return self.socket.recv(2048).decode()


def is_init_data_valid(init_data: list[str]) -> bool:
    if len(init_data) != 3: return False
    client_id, fen_str, time_left = init_data
    if not client_id.isnumeric(): return False
    if not time_left.isnumeric(): return False
    data = fen_str.split()
    if len(data) != 6: return False
    fen_data = FenData(*data)
    if not validate_fen_data(fen_data): return False
    return True