import pytest

from utils.forsyth_edwards_notation import Fen
from chess.piece_movement import get_available_moves


def test_base_moves():
    assert len(get_available_moves('n', 36, Fen('8/8/8/8/8/8/8/8 w KQkq - 0 1'))) is 8


@pytest.mark.parametrize("from_index,is_white_turn", [(1, False), (5, False), (62, True), (57, True)])
def test_default_fen(from_index: int, is_white_turn: bool):
    assert len(get_available_moves('n', from_index, Fen(), is_white_turn)) == 2


def test_fully_blocked():
    assert len(get_available_moves('n', 36, Fen('8/8/3p1p2/2p3p1/4k3/2p3p1/3p1p2/8 b KQkq - 0 1'))) == 0


def test_jump_over_piece():
    assert (len(get_available_moves('n', 36, Fen('8/8/3P1P2/2PpppP1/3pkp2/2PpppP1/3P1P2/8 b KQkq - 0 1'))) == 4)


def test_possible_take():
    fen = Fen('8/8/3P1P2/2P3P1/4k3/2P3P1/3P1P2/8 b KQkq - 0 1')
    moves = get_available_moves('n', 36, fen)
    assert len(moves) == 4
    for move in moves:
        assert fen[move].isupper()
