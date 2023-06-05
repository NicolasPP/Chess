from database.models import User
from network.client.chess_client import ChessClient
from config.user_config import UserConfig


class LauncherUser:
    user: User | None = None
    client: ChessClient | None = None

    @staticmethod
    def log_in(user: User) -> None:
        LauncherUser.user = user
        LauncherUser.client = ChessClient(UserConfig.get().data.server_ip, user)

    @staticmethod
    def get_user() -> User:
        if LauncherUser.user is None:
            raise Exception('user not logged in')
        return LauncherUser.user

    @staticmethod
    def get_client() -> ChessClient:
        if LauncherUser.client is None:
            raise Exception('user not logged in')
        return LauncherUser.client

    @staticmethod
    def log_out() -> None:
        LauncherUser.user = None
        LauncherUser.client = None
