from __future__ import annotations
import _thread as thread
import socket as skt
import enum
import typing

from chess.timer.timer_config import DefaultConfigs
from chess.game.chess_match import Match, MatchResult
from chess.network.chess_network import Net
from chess.network.command_manager import CommandManager, Command, ServerCommand
from chess.notation.forsyth_edwards_notation import encode_fen_data
from chess.movement.piece_movement import PieceMovement
from chess.board.side import Side
from chess.chess_logging import set_up_logging
from config import *

'''
[Errno 48] Address already in use
you can get the process ID with port with this command : sudo lsof -i:PORT
'''

logger = set_up_logging(SERVER_NAME, SERVER_LOG_FILE)


class ServerControlCommands(enum.Enum):
    SHUT_DOWN = enum.auto()
    END_GAME = enum.auto()

    def get_one_word(self) -> str:
        one_word: str = self.name
        return one_word.replace("_", "")

    @staticmethod
    def get(name: str) -> ServerControlCommands | None:
        command: ServerControlCommands | None = None
        try:
            command = ServerControlCommands[name]
        finally:
            return command

    @staticmethod
    def get_command_from_input(input_command: str) -> ServerControlCommands | None:
        input_command = input_command.strip()
        command: ServerControlCommands | None
        if input_command.__contains__('_'):

            return ServerControlCommands.get(input_command.upper())
        elif input_command.__contains__(' '):
            if input_command.count(' ') > 1:
                index = input_command.find(" ")
                input_command = input_command.replace(" ", "")
                input_command = input_command[:index] + '_' + input_command[index:]
            return ServerControlCommands.get("_".join(input_command.split(' ')).upper())

        else:
            if input_command.upper() == ServerControlCommands.SHUT_DOWN.get_one_word():
                return ServerControlCommands.SHUT_DOWN

            elif input_command.upper() == ServerControlCommands.END_GAME.get_one_word():
                return ServerControlCommands.END_GAME

            else:
                return None


class Server(Net):

    @staticmethod
    def send_all_bytes(connections: list[skt.socket], data: bytes) -> None:
        for client_socket in connections:
            client_socket.send(data)

    def __init__(self, server_ip: str):
        super().__init__(server_ip)
        self.client_id: int = -1
        self.match: Match = Match(DefaultConfigs.BLITZ_5)
        self.client_sockets: list[skt.socket] = []
        self.is_running: bool = False
        PieceMovement.load()

    def start(self) -> None:
        logger.info('Server started')
        try:
            self.socket.setsockopt(skt.SOL_SOCKET, skt.SO_REUSEADDR, 1)
            self.socket.bind(self.address)
        except skt.error as e:
            logger.debug("error binding : %s", e)
            return

        self.set_is_running(True)
        self.socket.listen()

        print("Waiting for clients to connect")
        logger.info("Waiting for clients to connect")

    def set_is_running(self, is_running: bool) -> None:
        self.is_running = is_running

    def get_is_running(self) -> bool:
        return self.is_running

    def run(self) -> None:
        self.start()
        thread.start_new_thread(game_logic, (self,))
        thread.start_new_thread(server_control_command_parser, (self,))
        while self.get_is_running():
            client_socket: skt.socket | None = None
            address: typing.Any = None
            try:
                client_socket, address = self.socket.accept()
            except OSError as e:
                logger.debug("%s", e)

            if client_socket is None or address is None:
                return

            print(f"Connected to address : {address}")
            logger.info("Connected to address : %s", address)

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
    while server.get_is_running():
        if server.match.update_fen and len(server.match.commands) > 0:
            data: bytes = CommandManager.serialize_command_list(server.match.commands)
            Server.send_all_bytes(server.client_sockets, data)
            server.match.update_fen = False
            server.match.commands = []
    return


def client_listener(client_socket: skt.socket, server: Server):
    with client_socket:
        p_id = server.client_init(client_socket)
        while server.get_is_running():
            try:
                data: bytes = client_socket.recv(DATA_SIZE)
            except ConnectionResetError as error:
                logger.debug("connection error: %s", error)
                server.set_is_running(False)
                break

            if not data:
                logger.debug("invalid data")
                server.set_is_running(False)
                break

            commands: list[Command] = []

            command: Command = CommandManager.deserialize_command_bytes(data)

            logger.debug("client : %s, sent move %s to server", p_id, command.name)

            commands = server.match.process_client_command(command, commands)

            server.match.update_fen = True
            server.match.commands = commands

    server.client_sockets.remove(client_socket)
    client_socket.close()

    print(f'client : {p_id}  disconnected')
    logger.info("client : %s  disconnected", p_id)
    return


def server_control_command_parser(server: Server) -> None:
    while server.get_is_running():
        input_command = input()
        command: ServerControlCommands | None = ServerControlCommands.get_command_from_input(input_command)
        if command is None:
            print("command not recognised")
        else:
            process_server_control_command(command, server)
    return


def process_server_control_command(command: ServerControlCommands, server: Server) -> None:
    end_game_info: dict[str, str] = {CommandManager.game_result_type: MatchResult.DRAW.name}
    if command is ServerControlCommands.SHUT_DOWN:
        server.set_is_running(False)
        server.socket.close()
        end_game_info[CommandManager.game_result] = "SERVER IS SHUTTING DOWN"
        end_game = CommandManager.get(ServerCommand.END_GAME, end_game_info)
        data = CommandManager.serialize_command_list([end_game])
        Server.send_all_bytes(server.client_sockets, data)

    if command is ServerControlCommands.END_GAME:
        end_game_info[CommandManager.game_result] = "SERVER SAID NO MORE"
        end_game = CommandManager.get(ServerCommand.END_GAME, end_game_info)
        data = CommandManager.serialize_command_list([end_game])
        Server.send_all_bytes(server.client_sockets, data)


if __name__ == '__main__':
    Server('').run()
