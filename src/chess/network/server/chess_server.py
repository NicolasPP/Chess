from __future__ import annotations
import socket as skt
import enum
import logging
import threading

from chess.network.chess_network import Net
from chess.chess_logging import set_up_logging, LoggingOut
from chess.network.server.server_user import ServerUser
from chess.network.commands.command import Command
from chess.network.commands.command_manager import CommandManager
from config.pg_config import *

'''
[Errno 48] Address already in use
you can get the process ID with port with this command : sudo lsof -i:PORT
'''


class ChessServer(Net):
    def __init__(self) -> None:
        super().__init__('')
        self.is_running: bool = False
        self.logger: logging.Logger = set_up_logging(SERVER_NAME, LoggingOut.STDOUT, SERVER_LOG_FILE, logging.INFO)
        self.users: list[ServerUser] = []
        self.server_control_thread: threading.Thread = threading.Thread(target=self.server_control_command_parser)

    def start(self) -> None:
        self.logger.info('Server started')
        try:
            self.socket.setsockopt(skt.SOL_SOCKET, skt.SO_REUSEADDR, 1)
            self.socket.bind(self.address)
        except skt.error as e:
            self.logger.error("error binding due to: %s", e)
            return

        self.set_is_running(True)
        self.socket.listen()

        self.logger.info("Waiting for clients to connect")

    def accept_user(self) -> ServerUser | None:
        try:
            return ServerUser(*self.socket.accept())
        except OSError as err:
            if self.get_is_running():
                self.logger.error("could not accept client connection due to: %s", err)
            return None

    def set_is_running(self, is_running: bool) -> None:
        self.is_running = is_running

    def get_is_running(self) -> bool:
        return self.is_running

    def run(self) -> None:
        self.start()
        self.server_control_thread.start()
        while self.get_is_running():

            user: ServerUser = self.accept_user()
            if user is None and not self.get_is_running(): return

            self.logger.info("Connected to address : %s", user.address)
            t = threading.Thread(target=self.user_listener, args=(user,))
            t.start()
            self.users.append(user)

    def server_control_command_parser(self) -> None:
        while self.get_is_running():
            input_command = input()
            command: ServerControlCommands | None = ServerControlCommands.get_command_from_input(input_command)
            if command is None:
                print('hello')
                self.logger.info("command %s not recognised", input_command)
            else:
                self.process_server_control_command(command)
        return

    def process_server_control_command(self, command: ServerControlCommands) -> None:
        if command is ServerControlCommands.SHUT_DOWN:
            self.set_is_running(False)
            self.socket.close()

    def user_listener(self, user: ServerUser):
        with user.socket:
            while self.get_is_running():
                try:
                    data: bytes = user.socket.recv(DATA_SIZE)
                except ConnectionResetError as error:
                    self.logger.debug("connection error: %s", error)
                    self.set_is_running(False)
                    break

                if not data:
                    self.logger.debug("invalid data")
                    self.set_is_running(False)
                    break

                commands: list[Command] = []
                command: Command = CommandManager.deserialize_command_bytes(data)

        self.users.remove(user)
        user.socket.close()
        self.logger.info("client disconnected")


class ServerControlCommands(enum.Enum):
    SHUT_DOWN = enum.auto()

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

            else:
                return None


if __name__ == "__main__":
    server: ChessServer = ChessServer()
    server.run()
