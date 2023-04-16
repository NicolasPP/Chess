from __future__ import annotations
import string

from config import *


class AlgebraicNotation:
    @staticmethod
    def get_index_from_an(file: str, rank: str) -> int:
        validate_file_and_rank(file, rank)
        ascii_str = string.ascii_lowercase
        return ((BOARD_SIZE - int(rank)) * BOARD_SIZE) + ascii_str.index(file)

    @staticmethod
    def get_an_from_index(index: int) -> AlgebraicNotation:
        if index < 0: raise IndexError("index cannot be negative")
        if index > 63: raise IndexError("index cannot be above 63")
        row_num, col_num = divmod(index, BOARD_SIZE)
        ascii_str = string.ascii_lowercase
        return AlgebraicNotation(ascii_str[col_num], str(BOARD_SIZE - row_num))

    def __init__(self, file: str, rank: str):
        validate_file_and_rank(file, rank)
        self.file: str = file
        self.rank: str = rank
        self.coordinates: str = file + rank
        self.index: int = AlgebraicNotation.get_index_from_an(file, rank)


def validate_file_and_rank(file: str, rank: str) -> bool:
    if len(file) != 1 or \
            len(rank) != 1: raise Exception("cannot be empty or larger than 1 char")
    if file.isnumeric(): raise Exception("col should be letter")
    if not rank.isnumeric(): raise Exception("row should be number")
    if int(rank) > BOARD_SIZE or file > 'h': raise Exception("invalid index")
    return True
