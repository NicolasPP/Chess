import _thread as thread
import logging
import socket as skt

from chess.piece_movement import PieceMovement, Side
from chess.match import MoveTags, Match
from utils.forsyth_edwards_notation import encode_fen_data
from utils.command_manager import CommandManager, Command, ServerCommand
from utils.network import Net
from chess.chess_timer import DefaultConfigs

from config import *

'''
[Errno 48] Address already in use
you can get the process ID with port with this command : sudo lsof -i:PORT
'''

logging.basicConfig(
    filename='../Chess/log/server.log',
    encoding='utf-8',
    level=logging.DEBUG,
    filemode='w',
    format='%(asctime)s\t%(levelname)s\t%(message)s'
)


class Server(Net):

    @staticmethod
    def send_all(connections: list[skt.socket], data: str) -> None:
        for client_socket in connections:
            client_socket.send(str.encode(data))

    @staticmethod
    def send_all_bytes(connections: list[skt.socket], data: bytes) -> None:
        for client_socket in connections:
            client_socket.send(data)

    def __init__(self, server_ip: str):
        super().__init__(server_ip)
        self.client_id: int = -1
        self.match: Match = Match(DefaultConfigs.BLITZ_5)
        self.client_sockets: list[skt.socket] = []
        PieceMovement.load_pieces_info()

    def start(self) -> None:
        logging.info('Server started')
        try:
            self.socket.setsockopt(skt.SOL_SOCKET, skt.SO_REUSEADDR, 1)
            self.socket.bind(self.address)
        except skt.error as e:
            logging.debug("error binding : %s", e)

        self.socket.listen()

        print("Waiting for clients to connect")
        logging.info("Waiting for clients to connect")

    def run(self) -> None:
        self.start()
        thread.start_new_thread(game_logic, (self,))
        while True:
            client_socket, addr = self.socket.accept()
            print(f"Connected to address : {addr}")
            logging.info("Connected to address : %s", addr)

            self.client_sockets.append(client_socket)
            thread.start_new_thread(client_listener, (client_socket, self,))

    def get_id(self) -> str:
        self.client_id += 1
        return str(self.client_id)

    def client_init(self, client_socket: skt.socket) -> str:
        client_id = self.get_id()
        side_name = Side.WHITE.name if int(client_id) % 2 == 0 else Side.BLACK.name
        init_info: dict[str, str] = {
            CommandManager.side: side_name,
            CommandManager.fen_notation: encode_fen_data(self.match.fen.data),
            CommandManager.time: str(self.match.timer_config.time)
        }
        init: Command = CommandManager.get(ServerCommand.INIT_INFO, init_info)
        Server.send_all_bytes([client_socket], CommandManager.serialize_command(init))
        return client_id


def game_logic(server: Server):
    while True:
        if server.match.update_fen and len(server.match.commands) > 0:
            data: bytes = CommandManager.serialize_command_list(server.match.commands)
            Server.send_all_bytes(server.client_sockets, data)
            server.match.update_fen = False
            server.match.commands = []


def client_listener(client_socket: skt.socket, server: Server):
    with client_socket:
        p_id = server.client_init(client_socket)
        while True:
            data: bytes = client_socket.recv(DATA_SIZE)
            if not data: break
            commands: list[Command] = []
            move_tags: list[MoveTags] = []

            command: Command = CommandManager.deserialize_command_bytes(data)

            logging.debug("client : %s, sent move %s to server", p_id, command.name)

            move_tags, commands = server.match.process_client_command(command, move_tags, commands)

            logging.debug("move tags : %s", str(move_tags))

            server.match.update_fen = True
            server.match.commands = commands

        server.client_sockets.remove(client_socket)

        print(f'client : {p_id}  disconnected')
        logging.info("client : %s  disconnected", p_id)


if __name__ == '__main__':
    Server('').run()
