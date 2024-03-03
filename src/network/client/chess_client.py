import logging
import socket as skt
import typing
from _thread import start_new_thread

from chess.chess_player import Player
from config.logging_manager import AppLoggers
from config.logging_manager import LoggingManager
from config.pg_config import DATA_SIZE
from config.tk_config import SERVER_SHUT
from database.models import User
from event.event import Event
from event.event import EventContext
from event.event import EventType
from event.event_manager import EventManager
from event.game_events import EndGameEvent
from event.game_events import GameEvent
from event.launcher_events import DisconnectEvent
from event.launcher_events import EnterQueueEvent
from event.launcher_events import LaunchGameEvent
from event.launcher_events import LauncherEvent
from event.launcher_events import ServerVerificationEvent
from launcher.pg.pg_launcher import ChessPygameLauncher
from launcher.tk.global_vars import GlobalUserVars
from network.chess_network import Net


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

    def run(self) -> None:
        while self.get_is_connected():
            event_bytes: bytes | None = self.read()
            if event_bytes is None or not event_bytes:
                break

            events: list[Event] = EventManager.load_events(event_bytes)
            for event in events:
                if event.context is EventContext.LAUNCHER:
                    process_launcher_events(event)

                elif event.context is EventContext.GAME:
                    process_game_events(event)

                self.logger.info("server sent %s command", event.type.name)

    def server_listener(self) -> None:
        with self.socket:
            self.send_verification()
            self.run()
        self.logger.info("server disconnected")

    def send_verification(self) -> None:
        EventManager.dispatch(self.socket,
                              ServerVerificationEvent(self.user.u_name, self.user.elo, self.user.u_id,
                                                      self.user.u_pass))

    def send_queue_request(self) -> None:
        EventManager.dispatch(self.socket, EnterQueueEvent())


def process_launcher_events(launcher_event: Event) -> None:
    if ChessPygameLauncher.get().is_running:
        return

    assert isinstance(launcher_event, LauncherEvent)

    if launcher_event.type is EventType.DISCONNECT:
        assert isinstance(launcher_event, DisconnectEvent)
        GlobalUserVars.get().get_var(GlobalUserVars.connect_error).set(launcher_event.reason)
        GlobalUserVars.get().get_var(GlobalUserVars.server_disconnect).set(True)

    elif launcher_event.type is EventType.LAUNCH_GAME:
        assert isinstance(launcher_event, LaunchGameEvent)
        launch_string: str = "-".join([str(launcher_event.time), launcher_event.side, str(launcher_event.match_id)])
        GlobalUserVars.get().get_var(GlobalUserVars.launch_game).set(launch_string)


def process_game_events(game_event: Event) -> None:
    if (player := ChessPygameLauncher.get().multi_player.player) is None:
        return

    assert isinstance(game_event, GameEvent)

    Player.process_game_event(game_event, ChessPygameLauncher.get().multi_player.match_fen, player)

    if not isinstance(game_event, EndGameEvent):
        return

    if game_event.reason != SERVER_SHUT:
        return

    GlobalUserVars.get().get_var(GlobalUserVars.connect_error).set(SERVER_SHUT)
    GlobalUserVars.get().get_var(GlobalUserVars.server_disconnect).set(True)
