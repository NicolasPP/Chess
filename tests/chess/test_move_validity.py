import pytest

from src.utils.forsyth_edwards_notation import Fen
import src.chess.validate_move as validate_move


@pytest.mark.parametrize("from_fen_val,is_white_turn,expected",
                         [('p', True, False), ('P', True, True), ('p', False, True), ('P', False, False)])
def test_is_from_correct_side(from_fen_val: str, is_white_turn: bool, expected: bool):
    assert validate_move.is_from_correct_side(from_fen_val, is_white_turn) is expected


@pytest.mark.parametrize("from_index,dest_index,fen,expected", [
    (28, 20, Fen("8/8/8/4P3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 1, Fen("8/8/8/4B3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 7, Fen("8/8/8/4B3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 55, Fen("8/8/8/4B3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 56, Fen("8/8/8/4B3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 4, Fen("8/8/8/4R3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 24, Fen("8/8/8/4R3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 31, Fen("8/8/8/4R3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 60, Fen("8/8/8/4R3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 11, Fen("8/8/8/4N3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 13, Fen("8/8/8/4N3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 18, Fen("8/8/8/4N3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 22, Fen("8/8/8/4N3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 34, Fen("8/8/8/4N3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 38, Fen("8/8/8/4N3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 43, Fen("8/8/8/4N3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 45, Fen("8/8/8/4N3/8/8/8/8 w KQkq - 0 1"), True),
])
def test_is_destination_valid(from_index: int, dest_index: int, fen: Fen, expected: bool):
    assert validate_move.is_destination_valid(from_index, dest_index, fen) is expected


@pytest.mark.parametrize("from_index,dest_index,fen,expected", [
    (1, 1, Fen(), False),
    (0, 1, Fen(), False),
    (0, 63, Fen(), True),
    (4, 0, Fen("r3k2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1"), True)
])
def test_is_side_valid(from_index: int, dest_index: int, fen: Fen, expected: bool):
    assert validate_move.is_side_valid(from_index, dest_index, fen) is expected


@pytest.mark.parametrize("fen,from_index,expected", [
    (Fen(), 16, False),
    (Fen(), 0, False),
    (Fen(), 63, True)

])
def is_from_valid(fen: Fen, from_index: int, expected: bool):
    assert validate_move.is_from_valid(fen, from_index) is expected


@pytest.mark.parametrize("from_index,dest_index,fen,expected", [
    (48, 32, Fen(), True),
    (48, 24, Fen(), False),
    (28, 1, Fen("8/8/8/4B3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 7, Fen("8/8/8/4B3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 55, Fen("8/8/8/4B3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 56, Fen("8/8/8/4B3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 4, Fen("8/8/8/4R3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 24, Fen("8/8/8/4R3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 31, Fen("8/8/8/4R3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 60, Fen("8/8/8/4R3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 11, Fen("8/8/8/4N3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 13, Fen("8/8/8/4N3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 18, Fen("8/8/8/4N3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 22, Fen("8/8/8/4N3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 34, Fen("8/8/8/4N3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 38, Fen("8/8/8/4N3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 43, Fen("8/8/8/4N3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 45, Fen("8/8/8/4N3/8/8/8/8 w KQkq - 0 1"), True),
])
def test_is_move_valid(from_index: int, dest_index: int, fen: Fen, expected: bool):
    assert validate_move.is_move_valid(from_index, dest_index, fen) is expected
