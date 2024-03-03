from __future__ import annotations
import enum


class Side(enum.Enum):
    WHITE = enum.auto()
    BLACK = enum.auto()

    def get_opposite(self) -> Side:
        side: Side = Side[self.name]

        if side is Side.WHITE:
            return Side.BLACK

        if side is Side.BLACK:
            return Side.WHITE

        else:
            raise Exception
