import pytest

import utils.FEN_notation as FEN
import chess.game as GAME


def test_base_moves():
    assert len(GAME.get_available_moves('KING', 36, FEN.Fen('8/8/8/8/8/8/8/8'), True)) is 8


def test_blocked():
    assert len(GAME.get_available_moves('KING', 36, FEN.Fen('8/8/8/3PPP2/3PKP2/3PPP2/8/8'), True)) is 0


def test_possible_take():
    assert len(GAME.get_available_moves('KING', 36, FEN.Fen('8/8/8/3pPp2/3pKp2/3PPP2/8/8'), True)) is 4


@pytest.mark.parametrize("from_index,is_white_turn", [(4, False), (60, True)])
def test_default_fen(from_index: int, is_white_turn: bool):
    assert len(GAME.get_available_moves('KING', from_index, FEN.Fen(), is_white_turn)) is 0


@pytest.mark.xfail
def test_castle_while_in_check():
    assert len(GAME.get_available_moves('KING', 60, FEN.Fen('8/8/8/8/8/8/PPPPPpPP/R3K2R'), True)) is 3


@pytest.mark.xfail
def test_castle_into_check():
    assert len(GAME.get_available_moves('KING', 60, FEN.Fen('8/8/8/8/5q2/8/PPP2PPP/R3K2R'), True)) is 4


@pytest.mark.xfail
def test_castle_through_check():
    assert len(GAME.get_available_moves('KING', 60, FEN.Fen('8/8/8/8/2b5/8/PPP2PPP/R3K2R'), True)) is 3


@pytest.mark.xfail
def test_castle_blocked_by_piece():
    assert len(GAME.get_available_moves('KING', 60, FEN.Fen('8/8/8/8/8/8/PPP2PPP/R3K1NR'), True)) is 3

@pytest.mark.xfail
def test_base_castle():
    assert len(GAME.get_available_moves('KING', 60, FEN.Fen('8/8/8/8/8/8/PPPPPPPP/R3K2R'), True)) is 4

@pytest.mark.skip(reason="no way of currently testing this")
def test_castle_must_be_first_move():
    pass