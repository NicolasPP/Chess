from __future__ import annotations
import enum
import logging
import threading
import socket as skt
from _thread import start_new_thread

from network.chess_network import Net
from chess.chess_logging import set_up_logging, LoggingOut
from network.server.server_user import ServerUser
from network.commands.client_commands import ClientCommand
from network.commands.server_commands import ServerCommand
from network.commands.command import Command
from network.commands.command_manager import CommandManager
from database.chess_db import ChessDataBase, DataBaseInfo
from database.models import User
from config.pg_config import *
from config.tk_config import *

'''
[Errno 48] Address already in use
you can get the process ID with port with this command : sudo lsof -i:PORT
'''


class ChessServer(Net):

    server: ChessServer | None = None

    @staticmethod
    def get_host_ipv4() -> str:
        socket = skt.socket(skt.AF_INET, skt.SOCK_DGRAM)
        socket.settimeout(0)
        try:
            socket.connect(('10.254.254.254', 1))
            ipv4 = socket.getsockname()[0]
        except skt.error:
            ipv4 = '127.0.0.1'
        finally:
            socket.close()
        return ipv4

    @staticmethod
    def get() -> ChessServer:
        if ChessServer.server is None:
            ChessServer.server = ChessServer()
        return ChessServer.server

    @staticmethod
    def is_local_server_online() -> bool:
        try:
            socket: skt.socket = skt.socket(skt.AF_INET, skt.SOCK_STREAM)
            socket.connect(('', 3389))
            return True
        except skt.error:
            return False

    def __init__(self) -> None:
        super().__init__('')  # must be '' or other computers will not be able to join
        self.is_running: bool = False
        self.logger: logging.Logger = set_up_logging(SERVER_NAME, LoggingOut.STDOUT, SERVER_LOG_FILE, logging.INFO)
        self.users: list[ServerUser] = []
        self.server_control_thread: threading.Thread = threading.Thread(target=self.server_control_command_parser)
        self.database: ChessDataBase = ChessDataBase(
            DataBaseInfo(*LOCAL_CHESS_DB_INFO)
        )

    def start(self) -> bool:
        if ChessServer.is_local_server_online():
            self.logger.info("server is already running")
            return False
        try:
            self.socket.setsockopt(skt.SOL_SOCKET, skt.SO_REUSEADDR, 1)
            self.socket.bind(self.address)
        except skt.error as e:
            self.logger.error("error binding due to: %s", e)
            return False

        self.logger.info("Server started")
        self.logger.info("Waiting for clients to connect")
        self.socket.listen()
        self.set_is_running(True)

        return True

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

    def run(self, start_control_thread: bool = True) -> None:
        if not self.get_is_running():
            if not self.start(): return

        if start_control_thread:
            self.server_control_thread.start()

        while self.get_is_running():

            server_user: ServerUser | None = self.accept_user()
            if server_user is None: return

            if self.verify_user(server_user):
                self.users.append(server_user)
                self.logger.info("client: %s connected", server_user.get_db_user().u_name)
                start_new_thread(self.user_listener, (server_user,))
            else:
                server_user.socket.close()
                self.logger.info("could not verify user")

    def server_control_command_parser(self) -> None:
        while self.get_is_running():
            input_command: str = input()
            command: ServerControlCommands | None = ServerControlCommands.get_command_from_input(input_command)
            if command is None:
                self.logger.info("command %s not recognised", input_command)
            else:
                self.process_server_control_command(command)
        return

    def process_server_control_command(self, command: ServerControlCommands) -> None:
        if command is ServerControlCommands.SHUT_DOWN:
            self.shut_down()

    def user_listener(self, user: ServerUser) -> None:
        with user.socket:
            while self.get_is_running():
                try:
                    data: bytes = user.socket.recv(DATA_SIZE)
                except ConnectionResetError as error:
                    self.logger.debug("connection error: %s", error)
                    break

                if not data:
                    self.logger.debug("invalid data")
                    break

                command: Command = CommandManager.deserialize_command_bytes(data)
                self.logger.info("command : %s received from the client", command.name)

        self.users.remove(user)
        user.socket.close()
        assert user.db_user is not None, "user cannot be None, because at this point the user has been verified"
        self.logger.info("client: %s disconnected", user.db_user.u_name)
        return

    def shut_down(self) -> None:
        self.set_is_running(False)
        try:
            self.socket.shutdown(skt.SHUT_RDWR)
        except OSError: pass
        self.reset_socket()
        disconnect_info: dict[str, str] = {}
        disconnect: Command = CommandManager.get(ServerCommand.DISCONNECT, disconnect_info)
        self.send_all(disconnect)
        self.logger.info("telling clients to disconnect")
        self.logger.info("shutting down server")

    def send_all(self, command: Command) -> None:
        for user in self.users:
            user.socket.send(CommandManager.serialize_command(command))

    def verify_user(self, server_user: ServerUser) -> bool:
        verification_command: Command | None = self.receive_verification(server_user)

        if verification_command is None: return False
        if verification_command.name != ClientCommand.VERIFICATION.name:
            self.logger.info("initial command cannot be : %s", verification_command.name)
            return False

        db_user_name: str = verification_command.info[CommandManager.user_name]
        db_user: User | None = self.database.get_user(db_user_name)
        if db_user is None:
            self.logger.info("database could not find user : %s", db_user_name)
            return False

        for server_users in self.users:
            if server_users.get_db_user().u_name == db_user.u_name:
                self.logger.info("user : %s is already connected", db_user.u_name)
                return False

        return server_user.set_db_user(verification_command.info, db_user)

    def receive_verification(self, user: ServerUser) -> Command | None:
        try:
            data: bytes = user.socket.recv(DATA_SIZE)
        except ConnectionResetError as error:
            self.logger.debug("connection error: %s", error)
            return None

        if not data:
            self.logger.debug("invalid data")
            return None

        return CommandManager.deserialize_command_bytes(data)


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
