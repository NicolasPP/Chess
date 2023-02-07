import _thread as thread
import logging
import socket as skt

import click

import chess.match as MATCH
import utils.FEN_notation as FEN
import utils.commands as CMD
import utils.network as NET
from config import *

'''
[Errno 48] Address already in use
you can get the process ID with port with this command : sudo lsof -i:PORT
'''

logging.basicConfig(
    filename='log/server.log',
    encoding='utf-8',
    level=logging.DEBUG,
    filemode='w',
    format='%(asctime)s\t%(levelname)s\t%(message)s'
)


class Server(NET.Net):
    def __init__(self, server_ip: str):
        super().__init__(server_ip)
        self.client_id: int = -1
        self.match: MATCH.Match = MATCH.Match()
        self.client_sockets: list[skt.socket] = []

    def start(self) -> None:
        logging.info('Server started')
        print(f'server started at {self.server}')
        try:
            self.socket.setsockopt(skt.SOL_SOCKET, skt.SO_REUSEADDR, 1)
            self.socket.bind(self.address)
        except skt.error as e:
            logging.debug("error binding : %s", e)

        self.socket.listen()

        logging.info("Waiting for clients to connect")

    def run(self) -> None:
        self.start()
        thread.start_new_thread(game_logic, (self,))
        while True:
            client_socket, addr = self.socket.accept()
            logging.info("Connected to address : %s", addr)

            self.client_sockets.append(client_socket)
            thread.start_new_thread(client_listener, (client_socket, self,))

    def get_id(self) -> str:
        self.client_id += 1
        return str(self.client_id)

    def send_all_clients(self, data: str):
        for client_socket in self.client_sockets:
            client_socket.send(str.encode(data))


def game_logic(server: Server):
    while True:
        if server.match.update_pos:
            server.match.commands.append(END_MARKER)
            server.send_all_clients(C_SPLIT.join(server.match.commands))
            server.match.update_pos = False
            server.match.commands = []


def client_listener(client_socket: skt.socket, server: Server):
    with client_socket:
        p_id = server.get_id()
        client_socket.send(str.encode(p_id))
        client_socket.send(str.encode(FEN.encode_fen_data(server.match.fen.data)))
        while True:
            data: bytes = client_socket.recv(DATA_SIZE)
            if not data: break
            commands = []
            move_info = data.decode('utf-8')
            logging.debug("client : %s, sent move %s to server", p_id, move_info)
            move_type = server.match.process_move(move_info)
            logging.debug("move type : %s", move_type.name)

            # TODO change I_SPLIT.join(... into a function calling in commands script

            match move_type:
                case MATCH.MoveType.CHECK:
                    update_pos_command = CMD.get(CMD.COMMANDS.UPDATE_POS, server.match.fen.notation)
                    commands.append(update_pos_command.info)
                case MATCH.MoveType.CHECKMATE:
                    end_game_command = CMD.get(CMD.COMMANDS.END_GAME)
                    update_pos_command = CMD.get(CMD.COMMANDS.UPDATE_POS, server.match.fen.notation)
                    commands.append(end_game_command.info)
                    commands.append(update_pos_command.info)
                case MATCH.MoveType.REGULAR:
                    update_pos_command = CMD.get(CMD.COMMANDS.UPDATE_POS, server.match.fen.notation)
                    commands.append(update_pos_command.info)
                case MATCH.MoveType.INVALID:
                    invalid_move_command = CMD.get(CMD.COMMANDS.INVALID_MOVE)
                    commands.append(invalid_move_command.info)
                case _:
                    assert False, "INVALID MATCH.MOVE_TYPE"

            server.match.update_pos = True
            server.match.commands = commands

        server.client_sockets.remove(client_socket)
        logging.info("client : %s  disconnected", p_id)


@click.command()
@click.option('--ip', default='127.0.0.1', help='set ip address of server, default = 127.0.0.1')
def start_server(ip: str) -> None:
    Server(ip).run()


if __name__ == '__main__':
    start_server()
