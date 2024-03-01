from __future__ import annotations

import enum
import socket
import typing
from typing import Optional

from launcher.pg.offline_launcher import OfflineLauncher
from launcher.pg.online_launcher import OnlineLauncher


class SinglePlayerGameType(enum.Enum):
    HUMAN_VS_HUMAN = enum.auto()
    HUMAN_VS_BOT = enum.auto()
    BOT_VS_BOT = enum.auto()


class ChessPygameLauncher:

    chess_launcher: Optional[ChessPygameLauncher] = None

    @staticmethod
    def get() -> ChessPygameLauncher:
        if ChessPygameLauncher.chess_launcher is None:
            ChessPygameLauncher.chess_launcher = ChessPygameLauncher()

        return ChessPygameLauncher.chess_launcher

    def __init__(self):
        self.multi_player: OnlineLauncher = OnlineLauncher()
        self.single_player: OfflineLauncher = OfflineLauncher()
        self.is_running: bool = False
        self.show_app: typing.Callable[[], None] | None = None
        self.hide_app: typing.Callable[[], None] | None = None

    def set_show_app(self, show_app: typing.Callable[[], None]) -> None:
        self.show_app = show_app

    def set_hide_app(self, hide_app: typing.Callable[[], None]) -> None:
        self.hide_app = hide_app

    def get_is_running(self) -> bool:
        return self.is_running

    def launch_single_player(self, game_type: SinglePlayerGameType) -> None:
        if self.get_is_running():
            return
        self.is_running = True
        if self.hide_app is not None:
            self.hide_app()
        if game_type is SinglePlayerGameType.HUMAN_VS_HUMAN:
            self.single_player.launch_against_human()
        elif game_type is SinglePlayerGameType.BOT_VS_BOT:
            self.single_player.launch_bot_vs_bot()
        elif game_type is SinglePlayerGameType.HUMAN_VS_BOT:
            self.single_player.launch_against_bot()
        self.is_running = False
        if self.show_app is not None:
            self.show_app()

    def launch_multi_player_client(self, connection: socket.socket, time: float, side: str, match_id: int) -> None:
        if self.get_is_running():
            return
        self.is_running = True
        if self.hide_app is not None:
            self.hide_app()
        self.multi_player.launch(connection, time, side, match_id)
        self.is_running = False
        if self.show_app is not None:
            self.show_app()
