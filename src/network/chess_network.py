import socket as skt

from chess.board.side import Side
from chess_engine.notation.forsyth_edwards_notation import FenData
from chess_engine.notation.forsyth_edwards_notation import validate_fen_data
from network.commands.command import Command
from network.commands.command_manager import CommandManager


class Net:
    def __init__(self, server_ip):
        self.host = server_ip
        self.socket: skt.socket = skt.socket(skt.AF_INET, skt.SOCK_STREAM)
        self.port: int = 3389
        self.address: tuple[str, int] = (self.host, self.port)

    def set_ip_address(self, server_ip: str) -> None:
        self.host = server_ip
        self.address = (self.host, self.port)

    def reset_socket(self) -> None:
        self.socket.close()
        self.socket = skt.socket(skt.AF_INET, skt.SOCK_STREAM)


class ChessNetwork(Net):
    def __init__(self, server_ip: str):
        super().__init__(server_ip)

    def connect(self) -> Command:
        try:
            self.socket.connect(self.address)
        except skt.error as e:
            raise Exception(f"error connecting due to: {e}")
        init_data: bytes = self.read()
        init_info: Command = CommandManager.deserialize_command_bytes(init_data)

        if not is_init_data_valid(init_info):
            raise Exception("initial data corrupted, try connecting again")
        return init_info

    def read(self) -> bytes:
        return self.socket.recv(2048)


def is_init_data_valid(init_info: Command) -> bool:
    side = init_info.info[CommandManager.side]
    fen_str = init_info.info[CommandManager.fen_notation]
    time_left = init_info.info[CommandManager.time]
    if side != Side.WHITE.name and side != Side.BLACK.name: return False
    if not time_left.isnumeric(): return False
    data = fen_str.split()
    if len(data) != 6: return False
    fen_data = FenData(*data)

    is_valid = False
    try:
        is_valid = validate_fen_data(fen_data)
    finally:
        return is_valid
