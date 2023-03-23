import socket as skt
import typing
from chess.board import SIDE
from utils.forsyth_edwards_notation import FenData, validate_fen_data

from config import *


class ClientInitInfo(typing.NamedTuple):
    side: str
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

    def connect(self) -> ClientInitInfo:
        try:
            self.socket.connect(self.address)
        except skt.error as e:
            print(f'error connecting : {e}')
            raise Exception("error connecting")
        init_data = self.read().split(C_SPLIT)
        if not is_init_data_valid(init_data):
            raise Exception("initial data corrupted, try connecting again")
        return ClientInitInfo(*init_data)

    def read(self) -> str:
        return self.socket.recv(2048).decode()


def is_init_data_valid(init_data: list[str]) -> bool:
    if len(init_data) != 3: return False
    side, fen_str, time_left = init_data
    if side != SIDE.WHITE.name and side != SIDE.BLACK.name: return False
    if not time_left.isnumeric(): return False
    data = fen_str.split()
    if len(data) != 6: return False
    fen_data = FenData(*data)

    is_valid = False
    try:
        is_valid = validate_fen_data(fen_data)
    finally:
        return is_valid
