import logging
from random import shuffle

from database.chess_db import ChessDataBase
from database.models import User
from network.commands.client_commands import ClientLauncherCommand
from network.commands.command import Command
from network.commands.command_manager import CommandManager
from network.server.server_user import ServerUser


class ServerLobby:
    def __init__(self, logger: logging.Logger, database: ChessDataBase) -> None:
        self.logger: logging.Logger = logger
        self.database: ChessDataBase = database
        self.ready_to_play: list[ServerUser] = []
        self.users: set[ServerUser] = set()

    def enter_queue(self, server_user: ServerUser) -> None:
        self.ready_to_play.append(server_user)

    def add_user(self, server_user: ServerUser) -> None:
        assert server_user.db_user is not None, "user should already be verified"
        self.users.add(server_user)

    def get_match_ups(self) -> list[tuple[ServerUser, ServerUser]]:
        match_ups: list[tuple[ServerUser, ServerUser]] = []

        while len(self.ready_to_play) >= 2:
            shuffle(self.ready_to_play)
            match_ups.append((self.ready_to_play.pop(), self.ready_to_play.pop()))

        return match_ups

    def remove_user(self, server_user: ServerUser) -> None:
        if server_user not in self.users:
            self.logger.info("user: %s is not in the lobby", server_user.db_user.u_name)
            return

        self.users.remove(server_user)

    def get_connection_count(self) -> int:
        return len(self.users)

    def verify_user(self, server_user: ServerUser, verification_bytes: bytes | None) -> bool:
        if verification_bytes is None:
            return False

        verification_command: Command | None = CommandManager.deserialize_command_bytes(verification_bytes)

        if verification_command is None:
            return False
        if verification_command.name != ClientLauncherCommand.VERIFICATION.name:
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
