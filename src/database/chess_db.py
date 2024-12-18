import dataclasses
import enum
import hashlib
import logging

import sqlalchemy
from sqlalchemy import Select, and_, or_, text
from sqlalchemy.exc import DatabaseError, NoResultFound
from sqlalchemy.orm import Session

from config.logging_manager import AppLoggers, LoggingManager
from database.models import Game, User


@dataclasses.dataclass
class DataBaseInfo:
    user: str
    password: str
    host: str
    port: int
    database: str


'''
can restart mysql with WINDOWS + r services.msc
'''


class CreateUserResult(enum.Enum):
    SUCCESS = enum.auto()
    INVALID_USER_NAME = enum.auto()
    USER_NAME_TAKEN = enum.auto()
    INVALID_PASSWORD = enum.auto()


class CreateGameResult(enum.Enum):
    SUCCESS = enum.auto()
    INVALID_RESULT = enum.auto()
    INVALID_TIME_CONFIG = enum.auto()


class ChessDataBase:

    def __init__(self, db_info: DataBaseInfo) -> None:
        self.logger: logging.Logger = LoggingManager.get_logger(AppLoggers.DATABASE)
        self.db_info: DataBaseInfo = db_info
        self.engine: sqlalchemy.Engine | None = None

    def get_connection_url(self) -> str:
        return f"mysql+mysqlconnector://{self.db_info.user}:{self.db_info.password}@{self.db_info.host}:" \
               f"{self.db_info.port}/{self.db_info.database}"

    def create_engine(self) -> None:
        try:
            self.engine = sqlalchemy.create_engine(self.get_connection_url())
        except Exception as err:
            self.logger.error("engine could not be created due to : %s", err)

    def test_connection(self) -> bool:
        try:
            self.get_engine().connect()
            return True
        except DatabaseError as err:
            self.logger.error("could not connect to the database due to : %s", err)
            return False

    def log_in(self, user_name: str, user_password: str) -> User | None:
        user: User | None = self.get_user(user_name)
        if user is None: return None
        user_password_hash: str = hashlib.md5(user_password.encode('utf-8')).hexdigest()
        if user.u_pass != user_password_hash: return None
        return user

    def get_user(self, user_name: str) -> User | None:
        with Session(self.get_engine()) as session:
            try:
                user: User = session.scalars((Select(User).where(User.u_name == user_name))).one()
                return user
            except NoResultFound:
                return None

    def create_user(self, user_name: str, user_password: str) -> CreateUserResult:
        if not is_user_name_valid(user_name): return CreateUserResult.INVALID_USER_NAME
        if self.get_user(user_name) is not None: return CreateUserResult.USER_NAME_TAKEN
        if not is_user_password_valid(user_password): return CreateUserResult.INVALID_PASSWORD
        with Session(self.get_engine()) as session:
            session.add(User(u_pass=hashlib.md5(user_password.encode('utf-8')).hexdigest(), u_name=user_name))
            session.commit()
        return CreateUserResult.SUCCESS

    def create_game(self, white: User, black: User, moves: str, result: str, time_config: str, ) -> CreateGameResult:
        if len(result) > 7: return CreateGameResult.INVALID_RESULT
        if len(time_config) > 20: return CreateGameResult.INVALID_TIME_CONFIG

        with Session(self.get_engine()) as session:
            game: Game = Game(white_id=white.u_id, black_id=black.u_id, moves=moves, result=result,
                              time_config=time_config)
            winner, looser = get_winner_looser(result, white, black)

            queries: list[text] = [
                text(f"UPDATE users SET elo = {winner.elo + 10} WHERE u_id = {winner.u_id};"),
                text(f"UPDATE users SET elo = {looser.elo - 10} WHERE u_id = {looser.u_id};"),
            ]
            for query in queries:
                session.execute(query)

            session.add(game)
            session.commit()

        return CreateGameResult.SUCCESS

    def get_users_game(self, user: User, opp_user: User | None = None) -> list[Game]:
        result: list[Game] = []
        select: Select = Select(Game).filter(or_(Game.white_id == user.u_id, Game.black_id == user.u_id))

        if opp_user is not None:
            select = Select(Game).filter(
                or_(
                    and_(Game.white_id == user.u_id, Game.black_id == opp_user.u_id),
                    and_(Game.white_id == opp_user.u_id, Game.black_id == user.u_id)
                )
            )

        with Session(self.get_engine()) as session:
            for game in session.scalars(select).all():
                result.append(game)

        return result

    def get_engine(self) -> sqlalchemy.Engine:
        if self.engine is None: self.create_engine()
        assert self.engine is not None, "at this point we can be sure the engine has been created"
        return self.engine


def is_user_name_valid(user_name: str) -> bool:
    for char in user_name:
        if not char.isalnum() and not char.isspace():
            return False
    return True


def is_user_password_valid(user_password: str) -> bool:
    return len(user_password) > 0


def get_winner_looser(result: str, white: User, black: User) -> tuple[User, User]:
    if result == "WHITE":
        return white, black

    elif result == "BLACK":
        return black, white

    raise ValueError(f"Unexpected result: {result}")
