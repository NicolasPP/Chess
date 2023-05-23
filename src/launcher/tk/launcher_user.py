from database.models import User


class LauncherUser:
    user: User | None = None

    @staticmethod
    def log_in(user: User) -> None:
        LauncherUser.user = user

    @staticmethod
    def get_user() -> User:
        if LauncherUser.user is None:
            raise Exception('user not logged in')
        return LauncherUser.user

    @staticmethod
    def log_out() -> None:
        LauncherUser.user = None
