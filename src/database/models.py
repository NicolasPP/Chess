from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import ForeignKey, Text, String


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "Users"

    u_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    elo: Mapped[int] = mapped_column(default=0)
    u_pass: Mapped[str] = mapped_column(nullable=False)
    u_name: Mapped[str] = mapped_column(nullable=False)


class Game(Base):
    __tablename__ = "Games"

    g_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    white_id: Mapped[int] = mapped_column(ForeignKey("Users.u_id"), nullable=False)
    black_id: Mapped[int] = mapped_column(ForeignKey("Users.u_id"), nullable=False)
    moves: Mapped[str] = mapped_column(Text(), nullable=False)
    result: Mapped[str] = mapped_column(String(7), nullable=False)
    time_config: Mapped[str] = mapped_column(String(20), nullable=False)
