from __future__ import annotations

import enum
import logging
import socket as skt
import threading
from _thread import start_new_thread
from pickle import UnpicklingError
from typing import Optional
from uuid import uuid1

from chess.board.side import Side
from chess.game.chess_match import Match
from chess.game.chess_match import MatchResult
from chess.timer.timer_config import DefaultConfigs
from chess.timer.timer_config import TimerConfig
from config.logging_manager import AppLoggers
from config.logging_manager import LoggingManager
from config.pg_config import DATA_SIZE
from config.tk_config import LOCAL_CHESS_DB_INFO
from config.tk_config import MAX_CONNECTIONS
from config.tk_config import SERVER_SHUT
from database.chess_db import ChessDataBase
from database.chess_db import DataBaseInfo
from event.event import Event
from event.event import EventContext
from event.event import EventType
from event.event_manager import EventManager
from event.game_events import EndGameEvent
from event.game_events import GameEvent
from event.launcher_events import DisconnectEvent
from event.launcher_events import LaunchGameEvent
from network.chess_network import Net
from network.server.server_lobby import ServerLobby
from network.server.server_user import ServerUser

'''
[Errno 48] Address already in use
you can get the process ID with port with this command : sudo lsof -i:PORT
'''


class ServerMatch:
    def __init__(self, timer_config: TimerConfig, players: tuple[ServerUser, ServerUser]) -> None:
        self.match: Match = Match(timer_config)
        self.players: tuple[ServerUser, ServerUser] = players

    def get_sockets(self) -> tuple[skt.socket, skt.socket]:
        white, black = self.players
        return white.socket, black.socket


class ChessServer(Net):
    server: ChessServer | None = None
    database_info: DataBaseInfo = DataBaseInfo(*LOCAL_CHESS_DB_INFO)

    @staticmethod
    def get_host_ipv4() -> str:
        conn = skt.socket(skt.AF_INET, skt.SOCK_DGRAM)
        conn.settimeout(0)
        try:
            conn.connect(('10.254.254.254', 1))
            ipv4 = conn.getsockname()[0]
        except skt.error:
            ipv4 = '127.0.0.1'
        finally:
            conn.close()
        return ipv4

    @staticmethod
    def set_database_info(database_info: DataBaseInfo) -> None:
        ChessServer.database_info = database_info

    @staticmethod
    def get() -> ChessServer:
        if ChessServer.server is None:
            ChessServer.server = ChessServer()
        return ChessServer.server

    @staticmethod
    def is_local_server_online() -> bool:
        try:
            conn: skt.socket = skt.socket(skt.AF_INET, skt.SOCK_STREAM)
            conn.connect(('127.0.0.1', 3389))
            return True
        except skt.error:
            return False

    def __init__(self) -> None:
        super().__init__('')  # must be '' or other computers will not be able to join
        self.is_running: bool = False
        self.logger: logging.Logger = LoggingManager.get_logger(AppLoggers.SERVER)
        self.server_control_thread: threading.Thread = threading.Thread(target=self.server_control_command_parser)
        self.database: ChessDataBase = ChessDataBase(ChessServer.database_info)
        self.lobby: ServerLobby = ServerLobby(self.logger, self.database)
        self.matches: dict[int, ServerMatch] = {}

    def start(self, is_server_online: bool | None = None) -> bool:
        if is_server_online is None:
            if ChessServer.is_local_server_online():
                self.logger.info("server is already running")
                return False
        else:
            if is_server_online:
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
            if not self.start():
                return

        if start_control_thread:
            self.server_control_thread.start()

        while self.get_is_running():

            server_user: ServerUser | None = self.accept_user()
            if server_user is None:
                return

            verification: Optional[Event] = self.receive_verification(server_user)

            if self.lobby.get_connection_count() >= MAX_CONNECTIONS:
                EventManager.dispatch(server_user.socket, [DisconnectEvent("Too Many Connections")])

            elif self.lobby.verify_user(server_user, verification):
                self.lobby.add_user(server_user)
                self.logger.info("client: %s connected", server_user.get_db_user().u_name)
                start_new_thread(self.user_listener, (server_user,))

            else:
                EventManager.dispatch(server_user.socket, [DisconnectEvent("Could not verify user")])
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

    def user_listener(self, server_user: ServerUser) -> None:
        with server_user.socket:
            while self.get_is_running():
                try:
                    data: bytes = server_user.socket.recv(DATA_SIZE)
                except ConnectionResetError as error:
                    self.logger.debug("connection error: %s", error)
                    break

                if not data:
                    self.logger.debug("invalid data")
                    break

                event: Event = EventManager.load_event(data)
                self.logger.info("command : %s received from client %s", event.type.name,
                                 server_user.get_db_user().u_name)

                self.process_event(event, server_user)

        self.lobby.remove_user(server_user)
        server_user.socket.close()
        assert server_user.db_user is not None, "user cannot be None, because at this point the user has been verified"
        self.logger.info("client: %s disconnected", server_user.db_user.u_name)
        return

    def process_event(self, event: Event, server_user: ServerUser) -> None:
        if event.context is EventContext.LAUNCHER:
            self.process_in_launcher_event(event, server_user)

        elif event.context is EventContext.GAME:
            self.process_in_game_event(event)

    def process_in_launcher_event(self, event: Event, server_user: ServerUser) -> None:
        if event.type is EventType.ENTER_QUEUE:
            self.lobby.enter_queue(server_user)

            for players in self.lobby.get_match_ups():
                self.begin_match(uuid1(), *players)

        else:
            raise Exception(f"received unexpected event: {event.type}")

    def process_in_game_event(self, game_event: Event) -> None:
        assert isinstance(game_event, GameEvent), f"expected GAME context instead got: {game_event.context}"
        server_match: ServerMatch = self.matches[game_event.match_id]

        response: list[GameEvent] = server_match.match.process_game_event(game_event)

        for sock in server_match.get_sockets():
            EventManager.dispatch(sock, response)

    def begin_match(self, match_id: uuid1, white_player: ServerUser, black_player: ServerUser) -> None:
        server_match: ServerMatch = ServerMatch(DefaultConfigs.BLITZ_5_0, (white_player, black_player))
        self.matches[match_id.int] = server_match

        EventManager.dispatch(white_player.socket,
                              [LaunchGameEvent(match_id.int, server_match.match.timer_config.time, Side.WHITE.name)])
        EventManager.dispatch(black_player.socket,
                              [LaunchGameEvent(match_id.int, server_match.match.timer_config.time, Side.BLACK.name)])

    def shut_down(self) -> None:
        self.set_is_running(False)
        try:
            self.socket.shutdown(skt.SHUT_RDWR)
        except OSError:
            pass
        self.reset_socket()

        disconnect: DisconnectEvent = DisconnectEvent(SERVER_SHUT)
        end_game: EndGameEvent = EndGameEvent(-1, MatchResult.DRAW.name, SERVER_SHUT)
        for user in self.lobby.users:
            EventManager.dispatch(user.socket, [disconnect, end_game])
        self.logger.info("telling clients to disconnect")
        self.logger.info("shutting down server")

    def receive_verification(self, user: ServerUser) -> Optional[Event]:
        try:
            data: bytes = user.socket.recv(DATA_SIZE)
        except ConnectionResetError as error:
            self.logger.debug("connection error: %s", error)
            return None

        try:
            return EventManager.load_event(data)
        except UnpicklingError:
            return None

        except EOFError:
            return None


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
