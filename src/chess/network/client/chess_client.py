import logging
import socket as skt
from _thread import start_new_thread

from chess.chess_logging import set_up_logging, LoggingOut
from chess.network.chess_network import Net
from chess.network.commands.command_manager import CommandManager
from chess.network.commands.command import Command
from chess.network.commands.client_commands import ClientCommand
from database.models import User
from config.pg_config import *


class ChessClient(Net):
    def __init__(self, server_ip: str, user: User) -> None:
        super().__init__(server_ip)
        self.user: User = user
        self.logger: logging.Logger = set_up_logging(CLIENT_NAME, LoggingOut.STDOUT, CLIENT_LOG_FILE)
        self.is_connected: bool = False

    def start(self) -> bool:
        connect_result: bool = self.connect()
        if connect_result:
            self.set_is_connected(True)
            start_new_thread(self.server_listener, ())
        return connect_result

    def connect(self) -> bool:
        try:
            self.socket.connect(self.address)
            return True
        except skt.error as e:
            self.logger.error(f'error connecting : {e}')
            return False

    def disconnect(self) -> None:
        self.set_is_connected(False)
        self.reset_socket()

    def read(self) -> bytes | None:
        try:
            data = self.socket.recv(DATA_SIZE)
            return data
        except ConnectionResetError as err:
            self.logger.error("could not read data due to: %s", err)
            return None
        except OSError as err:
            self.logger.error("could not read data due to: %s", err)

    def get_is_connected(self) -> bool:
        return self.is_connected

    def set_is_connected(self, is_connected: bool) -> None:
        self.is_connected = is_connected

    def server_listener(self) -> None:
        with self.socket:
            self.send_verification()
            while self.get_is_connected():
                data_b: bytes | None = self.read()

                if data_b is None or not data_b:
                    break

                commands = CommandManager.deserialize_command_list_bytes(data_b)

                self.logger.debug("server sent commands :")
                for command in commands:
                    self.logger.debug(" - %s ", command.name)

            self.logger.info("server disconnected")
            return

    def send_verification(self) -> None:
        command_info: dict[str, str] = {CommandManager.user_name: self.user.u_name,
                                        CommandManager.user_elo: str(self.user.elo),
                                        CommandManager.user_id: str(self.user.u_id),
                                        CommandManager.user_pass: self.user.u_pass}
        command: Command = CommandManager.get(ClientCommand.VERIFICATION, command_info)
        self.socket.send(CommandManager.serialize_command(command))
