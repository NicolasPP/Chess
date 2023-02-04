import pytest

import utils.FEN_notation as FEN
import chess.game as GAME


def test_base_moves():
    assert len(GAME.get_available_moves('QUEEN', 36, FEN.Fen('8/8/8/8/8/8/8/8 w KQkq - 0 1'))) is 27


def test_fully_blocked():
    assert len(GAME.get_available_moves('QUEEN', 36, FEN.Fen('8/8/8/3ppp2/3pqp2/3ppp2/8/8 b KQkq - 0 1'))) is 0


def test_possible_take():
    fen = FEN.Fen('8/8/8/3PPP2/3PqP2/3PPP2/8/8 b KQkq - 0 1')
    moves = GAME.get_available_moves('QUEEN', 36, fen)
    assert len(moves) is 8
    for move in moves:
        assert fen[move].isupper()


def test_blocked_take():
    assert len(GAME.get_available_moves('QUEEN', 36, FEN.Fen('8/8/2P1P1P1/3ppp2/2PpqpP1/3ppp2/2P1P1P1/8 b KQkq - 0 1'))) is 0


def test_blocked_with_possible_take():
    fen = FEN.Fen('8/8/8/3PpP2/3Pqp2/3PpP2/8/8 b KQkq - 0 1')
    moves = GAME.get_available_moves('QUEEN', 36, fen)
    assert len(moves) is 5
    for move in moves:
        assert fen[move].isupper()


@pytest.mark.parametrize("from_index,is_white_turn", [(3, False), (59, True)])
def test_default_fen(from_index: int, is_white_turn: bool):
    assert len(GAME.get_available_moves('QUEEN', from_index, FEN.Fen(), is_white_turn)) is 0
