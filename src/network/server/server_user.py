import socket as skt

from database.models import User
from event.launcher_events import ServerVerificationEvent


class ServerUser:
    def __init__(self, socket: skt.socket, address: tuple[str, int]):
        self.socket: skt.socket = socket
        self.address: tuple[str, int] = address
        self.db_user: User | None = None

    def set_db_user(self, verification: ServerVerificationEvent, compare_user: User) -> bool:

        if any([compare_user.u_name != verification.user_name, compare_user.elo != verification.elo,
                compare_user.u_id != verification.id, compare_user.u_pass != verification.password]):
            return False

        self.db_user = compare_user
        return True

    def get_db_user(self) -> User:
        if self.db_user is None:
            raise Exception("user not verified yet")
        return self.db_user
