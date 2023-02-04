import pytest

import chess.game as GAME
import utils.FEN_notation as FEN


def test_first_turn_double_move(pawn_test_fen):
    from_index = 50
    assert len(GAME.get_available_moves('PAWN', from_index, pawn_test_fen)) is 2


def test_first_turn_double_move_and_possible_take(pawn_test_fen):
    from_index = 53
    assert len(GAME.get_available_moves('PAWN', from_index, pawn_test_fen)) is 3


def test_regular_move(pawn_test_fen):
    from_index = 41
    assert len(GAME.get_available_moves('PAWN', from_index, pawn_test_fen)) is 1


def test_blocked_by_piece(pawn_test_fen):
    from_index = 26
    assert len(GAME.get_available_moves('PAWN', from_index, pawn_test_fen)) is 0


def test_blocked_by_piece_and_possible_take(pawn_test_fen):
    from_index = 21
    assert len(GAME.get_available_moves('PAWN', from_index, pawn_test_fen)) is 1


def test_first_turn_double_move_blocked(pawn_test_fen):
    from_index = 55
    assert len(GAME.get_available_moves('PAWN', from_index, pawn_test_fen)) is 1


def test_first_turn_blocked(pawn_test_fen):
    from_index = 52
    assert len(GAME.get_available_moves('PAWN', from_index, pawn_test_fen)) is 0


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
    assert len(GAME.get_available_moves('PAWN', from_index, FEN.Fen(), is_white_turn)) is 2
