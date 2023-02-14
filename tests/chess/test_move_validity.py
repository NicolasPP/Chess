import pytest

import chess.game as GAME
import utils.Forsyth_Edwards_notation as FEN


@pytest.mark.parametrize("from_fen_val,is_white_turn,expected",
                         [('p', True, False), ('P', True, True), ('p', False, True), ('P', False, False)])
def test_is_from_correct_side(from_fen_val: str, is_white_turn: bool, expected: bool):
    assert GAME.is_from_correct_side(from_fen_val, is_white_turn) is expected


@pytest.mark.parametrize("from_index,dest_index,fen,expected", [
    (28, 20, FEN.Fen("8/8/8/4P3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 1, FEN.Fen("8/8/8/4B3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 7, FEN.Fen("8/8/8/4B3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 55, FEN.Fen("8/8/8/4B3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 56, FEN.Fen("8/8/8/4B3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 4, FEN.Fen("8/8/8/4R3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 24, FEN.Fen("8/8/8/4R3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 31, FEN.Fen("8/8/8/4R3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 60, FEN.Fen("8/8/8/4R3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 11, FEN.Fen("8/8/8/4N3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 13, FEN.Fen("8/8/8/4N3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 18, FEN.Fen("8/8/8/4N3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 22, FEN.Fen("8/8/8/4N3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 34, FEN.Fen("8/8/8/4N3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 38, FEN.Fen("8/8/8/4N3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 43, FEN.Fen("8/8/8/4N3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 45, FEN.Fen("8/8/8/4N3/8/8/8/8 w KQkq - 0 1"), True),
])
def test_is_destination_valid(from_index: int, dest_index: int, fen: FEN.Fen, expected: bool):
    assert GAME.is_destination_valid(from_index, dest_index, fen) is expected


@pytest.mark.parametrize("from_index,dest_index,fen,expected", [
    (1, 1, FEN.Fen(), False),
    (0, 1, FEN.Fen(), False),
    (0, 63, FEN.Fen(), True),
    (4, 0, FEN.Fen("r3k2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1"), True)
])
def test_is_side_valid(from_index: int, dest_index: int, fen: FEN.Fen, expected: bool):
    assert GAME.is_side_valid(from_index, dest_index, fen) is expected


@pytest.mark.parametrize("fen,from_index,expected", [
    (FEN.Fen(), 16, False),
    (FEN.Fen(), 0, False),
    (FEN.Fen(), 63, True)

])
def is_from_valid(fen: FEN.Fen, from_index: int, expected: bool):
    assert GAME.is_from_valid(fen, from_index) is expected


@pytest.mark.parametrize("from_index,dest_index,fen,expected", [
    (48, 32, FEN.Fen(), True),
    (48, 24, FEN.Fen(), False),
    (28, 1, FEN.Fen("8/8/8/4B3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 7, FEN.Fen("8/8/8/4B3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 55, FEN.Fen("8/8/8/4B3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 56, FEN.Fen("8/8/8/4B3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 4, FEN.Fen("8/8/8/4R3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 24, FEN.Fen("8/8/8/4R3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 31, FEN.Fen("8/8/8/4R3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 60, FEN.Fen("8/8/8/4R3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 11, FEN.Fen("8/8/8/4N3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 13, FEN.Fen("8/8/8/4N3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 18, FEN.Fen("8/8/8/4N3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 22, FEN.Fen("8/8/8/4N3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 34, FEN.Fen("8/8/8/4N3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 38, FEN.Fen("8/8/8/4N3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 43, FEN.Fen("8/8/8/4N3/8/8/8/8 w KQkq - 0 1"), True),
    (28, 45, FEN.Fen("8/8/8/4N3/8/8/8/8 w KQkq - 0 1"), True),
])
def test_is_move_valid(from_index: int, dest_index: int, fen: FEN.Fen, expected: bool):
    assert GAME.is_move_valid(from_index, dest_index, fen) is expected
