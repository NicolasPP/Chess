import socket as skt

from database.models import User
from chess.network.commands.command_manager import CommandManager


class ServerUser:
    def __init__(self, socket: skt.socket, address: tuple[str, int]):
        self.socket: skt.socket = socket
        self.address: tuple[str, int] = address
        self.db_user: User | None = None

    def set_db_user(self, verification_info: dict[str, str], compare_user: User) -> bool:
        result = verify_info(compare_user, verification_info)
        if not result: return result
        self.db_user = compare_user
        return result

    def get_db_user(self) -> User:
        if self.db_user is None:
            raise Exception("user not verified yet")
        return self.db_user


def verify_info(compare_user: User, verification_info: dict[str, str]) -> bool:
    if compare_user.u_name != verification_info[CommandManager.user_name]: return False
    if compare_user.elo != int(verification_info[CommandManager.user_elo]): return False
    if compare_user.u_id != int(verification_info[CommandManager.user_id]): return False
    if compare_user.u_pass != verification_info[CommandManager.user_pass]: return False
    return True
