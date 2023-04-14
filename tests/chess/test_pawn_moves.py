import pytest

from chess.notation.forsyth_edwards_notation import Fen, FenChars
from chess.movement.piece_movement import get_available_moves

fen = Fen("8/5pp1/2p2P2/2P5/7p/1P2p3/2P1PP1P/8 w KQkq - 0 1")


def test_first_turn_double_move():
    from_index = 50
    assert len(get_available_moves(from_index, fen)) is 2


def test_first_turn_double_move_and_possible_take():
    from_index = 53
    assert len(get_available_moves(from_index, fen)) is 3


def test_regular_move():
    from_index = 41
    assert len(get_available_moves(from_index, fen)) is 1


def test_blocked_by_piece():
    from_index = 26
    assert len(get_available_moves(from_index, fen)) is 0


def test_blocked_by_piece_and_possible_take():
    from_index = 21
    assert len(get_available_moves(from_index, fen)) is 1


def test_first_turn_double_move_blocked():
    from_index = 55
    assert len(get_available_moves(from_index, fen)) is 1


def test_first_turn_blocked():
    from_index = 52
    assert len(get_available_moves(from_index, fen)) is 0


@pytest.mark.parametrize("from_index,is_white_turn", [
    (8, False),
    (9, False),
    (10, False),
    (11, False),
    (12, False),
    (13, False),
    (14, False),
    (15, False),
    (55, True),
    (54, True),
    (53, True),
    (52, True),
    (51, True),
    (50, True),
    (49, True),
    (48, True)
])
def test_default_fen(from_index: int, is_white_turn: bool):
    assert len(get_available_moves(from_index, Fen(), is_white_turn)) is 2


def test_en_passant():
    f = Fen()
    expected = f[53]
    f.make_move(53, 37, f[53])
    assert f[37] == expected
    expected = f[13]
    f.make_move(13, 21, f[13])
    assert f[21] == expected
    expected = f[37]
    f.make_move(37, 29, f[37])
    assert f[29] == expected
    f.make_move(14, 30, f[14])
    assert len(get_available_moves(29, f)) == 1
    f.make_move(48, 40, f[48])
    assert len(get_available_moves(29, f, True)) == 0
    f.make_move(12, 28, f[12])
    assert len(get_available_moves(29, f)) == 1
    f.make_move(29, 20, f[29])
    assert f[28] == FenChars.BLANK_PIECE.value
    assert f[20] == 'P'
    f = Fen("rnbqkbnr/1ppppp2/7P/p7/8/8/PPPPPPP1/RNBQKBNR w KQkq a6 0 6")
    assert len(get_available_moves(23, f)) == 1
    f = Fen("rnbqkbnr/ppppppp1/8/8/P7/2N4p/1PPPPP2/R1BQKBNR b KQkq a3 0 7")
    assert len(get_available_moves(47, f)) == 1
