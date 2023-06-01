import threading
import logging
import socket as skt

from chess.chess_logging import set_up_logging, LoggingOut
from chess.network.chess_network import Net
from chess.network.commands.command_manager import CommandManager
from config.pg_config import *


class ChessClient(Net):
    def __init__(self, server_ip: str) -> None:
        super().__init__(server_ip)
        self.logger: logging.Logger = set_up_logging(CLIENT_NAME, LoggingOut.STDOUT, CLIENT_LOG_FILE)
        self.server_listener_thread: threading.Thread = threading.Thread(target=self.server_listener)

    def start(self) -> None:
        connect_result: bool = self.connect()
        self.server_listener_thread.start()

    def connect(self) -> bool:
        try:
            self.socket.connect(self.address)
            return True
        except skt.error as e:
            self.logger.error(f'error connecting : {e}')
            return False

    def read(self) -> bytes | None:
        try:
            return self.socket.recv(DATA_SIZE)
        except ConnectionResetError as err:
            self.logger.error("could not read data due to: %s", err)
            return None

    def server_listener(self) -> None:
        with self.socket:
            while True:
                data_b: bytes | None = self.read()
                if data_b is None or not data_b: break
                commands = CommandManager.deserialize_command_list_bytes(data_b)

                self.logger.debug("server sent commands :")
                for command in commands:
                    self.logger.debug(" - %s ", command.name)

            self.logger.info("server disconnected")
            return


if __name__ == "__main__":
    client: ChessClient = ChessClient("127.0.0.1")
    client.start()