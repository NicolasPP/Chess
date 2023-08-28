import logging
import socket as skt
import typing
from _thread import start_new_thread

from config.logging_manager import AppLoggers
from config.logging_manager import LoggingManager
from config.pg_config import DATA_SIZE
from database.models import User
from launcher.tk.global_vars import GlobalUserVars
from network.chess_network import Net
from network.commands.client_commands import ClientLauncherCommand
from network.commands.command import Command
from network.commands.command_manager import CommandManager
from network.commands.server_commands import ServerLauncherCommand


class ClientConnectResult(typing.NamedTuple):
    result: bool
    error: skt.error | None


class ChessClient(Net):
    def __init__(self, server_ip: str, user: User) -> None:
        super().__init__(server_ip)
        self.user: User = user
        self.logger: logging.Logger = LoggingManager.get_logger(AppLoggers.CLIENT)
        self.is_connected: bool = False

    def start(self) -> ClientConnectResult:
        connect_result: ClientConnectResult = self.connect()
        if connect_result.result:
            self.set_is_connected(True)
            start_new_thread(self.server_listener, ())
        return connect_result

    def connect(self) -> ClientConnectResult:
        try:
            self.socket.connect(self.address)
            return ClientConnectResult(True, None)
        except skt.error as err:
            self.logger.error(f'error connecting : {err}')
            return ClientConnectResult(False, err)

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
            return None

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

                command: Command = CommandManager.deserialize_command_bytes(data_b)

                parse_server_command(command)

                self.logger.info("server sent %s command", command.name)

            self.logger.info("server disconnected")
            return

    def send_verification(self) -> None:
        command_info: dict[str, str] = {CommandManager.user_name: self.user.u_name,
                                        CommandManager.user_elo: str(self.user.elo),
                                        CommandManager.user_id: str(self.user.u_id),
                                        CommandManager.user_pass: self.user.u_pass}
        command: Command = CommandManager.get(ClientLauncherCommand.VERIFICATION, command_info)
        self.socket.send(CommandManager.serialize_command(command))


def parse_server_command(command: Command) -> None:
    if command.name == ServerLauncherCommand.DISCONNECT.name:
        GlobalUserVars.get().get_var(GlobalUserVars.connect_error).set(
            command.info[CommandManager.disconnect_reason]
        )
        GlobalUserVars.get().get_var(GlobalUserVars.server_disconnect).set(True)

    elif command.name == ServerLauncherCommand.UPDATE_CONNECTED_USERS.name:
        GlobalUserVars.get().get_var(GlobalUserVars.connected_users).set(
            command.info[CommandManager.connected_users_info]
        )

    else:
        raise Exception(f"command : {command} not recognised")
