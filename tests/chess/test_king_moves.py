import pytest

from chess.notation.forsyth_edwards_notation import Fen
from chess.movement.piece_movement import get_available_moves


def test_base_moves():
    assert len(get_available_moves(36, Fen('k7/8/8/8/4K3/8/8/8 w - - 0 1'))) is 8


def test_blocked():
    assert len(get_available_moves(36, Fen('k7/8/8/3PPP2/3PKP2/3PPP2/8/8 w - - 0 1'))) is 0


def test_possible_take():
    assert len(get_available_moves(36, Fen('k7/8/8/3pPp2/3pKp2/3PPP2/8/8 w - - 0 1'))) is 4


@pytest.mark.parametrize("from_index,is_white_turn", [(4, False), (60, True)])
def test_default_fen(from_index: int, is_white_turn: bool):
    assert len(get_available_moves(from_index, Fen(), is_white_turn)) is 0


def test_castle_while_in_check():
    assert len(get_available_moves(60, Fen('7k/8/8/8/8/8/PPPPPpPP/R3K2R w KQkq - 0 1'))) is 3


def test_castle_into_check():
    assert len(get_available_moves(60, Fen('7k/8/8/8/5q2/8/PPP2PPP/R3K2R w KQkq - 0 1'))) is 4


def test_castle_through_check():
    assert len(get_available_moves(60, Fen('7k/8/8/8/2b5/8/PPP2PPP/R3K2R w KQkq - 0 1'))) is 3


def test_castle_blocked_by_piece():
    assert len(get_available_moves(60, Fen('7k/8/8/8/8/8/PPP2PPP/R3K1NR w KQkq - 0 1'))) is 5


def test_base_castle():
    assert len(get_available_moves(60, Fen('7k/8/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1'))) is 4
