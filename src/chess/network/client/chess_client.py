import threading
import logging
import socket as skt

from chess.chess_logging import set_up_logging, LoggingOut
from chess.network.chess_network import Net
from chess.network.commands.command_manager import CommandManager
from chess.network.commands.command import Command
from chess.network.commands.client_commands import ClientCommand
from database.models import User
from database.chess_db import ChessDataBase, DataBaseInfo
from config.pg_config import *


class ChessClient(Net):
    def __init__(self, server_ip: str, user: User) -> None:
        super().__init__(server_ip)
        self.user: User = user
        self.logger: logging.Logger = set_up_logging(CLIENT_NAME, LoggingOut.STDOUT, CLIENT_LOG_FILE)
        self.server_listener_thread: threading.Thread = threading.Thread(target=self.server_listener)

    def start(self) -> None:
        connect_result: bool = self.connect()
        print(connect_result)
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
            data = self.socket.recv(DATA_SIZE)
            return data
        except ConnectionResetError as err:
            self.logger.error("could not read data due to: %s", err)
            return None

    def server_listener(self) -> None:
        with self.socket:
            self.send_verification()
            while True:
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

if __name__ == "__main__":
    db_info: DataBaseInfo = DataBaseInfo('root', 'chess-database', '35.197.134.140', 3306, 'chess_db')
    chess_db: ChessDataBase = ChessDataBase(db_info)
    user: User = chess_db.get_user("nicolas")

    client: ChessClient = ChessClient("127.0.0.1", user)
    client.start()
