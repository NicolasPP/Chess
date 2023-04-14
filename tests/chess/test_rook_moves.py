import pytest

from chess.notation.forsyth_edwards_notation import Fen
from chess.movement.piece_movement import get_available_moves


def test_base_moves():
    assert len(get_available_moves(36, Fen('8/8/8/8/4r3/8/8/8 b KQkq - 0 1'))) == 14


@pytest.mark.parametrize("from_index,is_white_turn", [(0, False), (7, False), (63, True), (56, True)])
def test_default_fen(from_index: int, is_white_turn: bool):
    assert len(get_available_moves(from_index, Fen(), is_white_turn)) is 0


def test_fully_blocked():
    assert len(get_available_moves(36, Fen('8/8/8/4p3/3prp2/4p3/8/8 b KQkq - 0 1'))) is 0


def test_possible_take():
    fen = Fen('8/8/8/4P3/3PrP2/4P3/8/8 b KQkq - 0 1')
    moves = get_available_moves(36, fen)
    assert len(moves) is 4
    for move in moves:
        assert fen[move].isupper()


def test_blocked_with_possible_take():
    fen = Fen('8/8/8/4P3/2PprpP1/4P3/8/8 b KQkq - 0 1')
    moves = get_available_moves(36, fen)
    assert len(moves) is 2
    for move in moves:
        assert fen[move].isupper()


def test_blocked_take():
    assert len(get_available_moves(36, Fen('8/8/4P3/4p3/2PprpP1/4p3/4P3/8 b KQkq - 0 1'))) is 0
