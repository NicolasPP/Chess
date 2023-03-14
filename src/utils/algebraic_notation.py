import dataclasses
import string

from src.config import *


@dataclasses.dataclass
class AlgebraicNotationData:
    file: str
    rank: str
    coordinates: str
    index: int


class AlgebraicNotation:
    def __init__(self, file: str, rank: str):
        validate_file_and_rank(file, rank)
        self.data = get_data(file, rank)


def get_data(file: str, rank: str) -> AlgebraicNotationData:
    coordinates = file + rank
    index = get_index_from_an(file, rank)
    return AlgebraicNotationData(file, rank, coordinates, index)


def get_index_from_an(file: str, rank: str) -> int:
    validate_file_and_rank(file, rank)
    ascii_str = string.ascii_lowercase
    return ((BOARD_SIZE - int(rank)) * BOARD_SIZE) + ascii_str.index(file)


def validate_file_and_rank(file: str, rank: str) -> bool:
    if len(file) != 1 or \
            len(rank) != 1: raise Exception("cannot be empty or larger than 1 char")
    if file.isnumeric(): raise Exception("col should be letter")
    if not rank.isnumeric(): raise Exception("row should be number")
    if int(rank) > BOARD_SIZE or file > 'h': raise Exception("invalid index")
    return True


def get_an_from_index(index: int) -> AlgebraicNotation:
    if index < 0: raise IndexError("index cannot be negative")
    if index > 63: raise IndexError("index cannot be above 63")
    row_num, col_num = divmod(index, BOARD_SIZE)
    ascii_str = string.ascii_lowercase
    return AlgebraicNotation(ascii_str[col_num], str(BOARD_SIZE - row_num))
