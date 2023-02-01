import pytest

import chess.game as GAME
import utils.FEN_notation as FEN


def test_base_moves():
    assert len(GAME.get_available_moves('BISHOP', 36, FEN.Fen('8/8/8/8/4b3/8/8/8'), False)) is 13


def test_possible_takes():
    assert len(GAME.get_available_moves('BISHOP', 36, FEN.Fen('8/8/8/3P1P2/4b3/3P1P2/8/8'), False)) is 4


def test_fully_blocked():
    assert len(GAME.get_available_moves('BISHOP', 36, FEN.Fen('8/8/8/3p1p2/4b3/3p1p2/8/8'), False)) is 0


def test_blocked_possible_take():
    assert len(GAME.get_available_moves('BISHOP', 36, FEN.Fen('8/8/8/3P1p2/4b3/3p1P2/8/8'), False)) is 2


def test_blocked_take():
    assert len(GAME.get_available_moves('BISHOP', 36, FEN.Fen('8/8/8/5p2/4b3/3p1p2/2P3P1/8'), False)) is 4


@pytest.mark.parametrize("from_index,is_white_turn", [(2, False), (5, False), (61, True), (58, True)])
def test_default_fen(from_index: int, is_white_turn: bool):
    assert len(GAME.get_available_moves('BISHOP', from_index, FEN.Fen(), is_white_turn)) is 0
