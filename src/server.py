import _thread as thread
import logging
import socket as skt

import click

import chess.piece as chess_piece
from chess.board import SIDE
from chess.match import MoveTags, Match
from utils.forsyth_edwards_notation import encode_fen_data
import utils.commands as command_manager
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

    def __init__(self, server_ip: str):
        super().__init__(server_ip)
        self.client_id: int = -1
        self.match: Match = Match(DefaultConfigs.RAPID_15_10)
        self.client_sockets: list[skt.socket] = []
        chess_piece.Pieces.load_pieces_info()

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
        side_name = SIDE.WHITE.name if int(client_id) % 2 == 0 else SIDE.BLACK.name
        data = C_SPLIT.join([
            side_name,
            encode_fen_data(self.match.fen.data),
            str(self.match.timer_config.time)
        ])
        client_socket.send(str.encode(data))
        return client_id


def game_logic(server: Server):
    while True:
        if server.match.update_fen:
            server.match.commands.append(command_manager.Command(END_MARKER))
            data: str = C_SPLIT.join(list(map(lambda cmd: cmd.info, server.match.commands)))
            Server.send_all(server.client_sockets, data)
            server.match.update_fen = False
            server.match.commands = []


def client_listener(client_socket: skt.socket, server: Server):
    with client_socket:
        p_id = server.client_init(client_socket)
        while True:
            data: bytes = client_socket.recv(DATA_SIZE)
            if not data: break
            commands = []
            move_info = data.decode('utf-8')

            print(f"client : {p_id}, sent move {move_info} to server")
            logging.debug("client : %s, sent move %s to server", p_id, move_info)

            move_tags: list[MoveTags] = server.match.process_move(move_info)

            print(f"move tags : ", *list(map(lambda m_tag: m_tag.name, move_tags)), sep=' ')
            logging.debug("move tags : %s", str(move_tags))

            for tag in move_tags:
                commands.extend(server.match.process_tag(tag))

            commands.extend(server.match.process_match_state(commands))

            server.match.update_fen = True
            server.match.commands = commands

        server.client_sockets.remove(client_socket)

        print(f'client : {p_id}  disconnected')
        logging.info("client : %s  disconnected", p_id)


@click.command()
@click.option('--ip', default='', help='set ip address of server, default = 127.0.0.1')
def start_server(ip: str) -> None:
    Server(ip).run()


if __name__ == '__main__':
    start_server()
