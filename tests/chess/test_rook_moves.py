import pytest

import chess.game as GAME
import utils.FEN_notation as FEN


def test_base_moves():
    assert len(GAME.get_available_moves('ROOK', 36, FEN.Fen('8/8/8/8/8/8/8/8 b KQkq - 0 1'))) == 14


@pytest.mark.parametrize("from_index,is_white_turn", [(0, False), (7, False), (63, True), (56, True)])
def test_default_fen(from_index: int, is_white_turn: bool):
    fen = FEN.Fen()
    if not is_white_turn: fen.data.active_color = fen.get_next_active_color()
    assert len(GAME.get_available_moves('ROOK', from_index, fen)) is 0


def test_fully_blocked():
    assert len(GAME.get_available_moves('ROOK', 36, FEN.Fen('8/8/8/4p3/3prp2/4p3/8/8 b KQkq - 0 1'))) is 0


def test_possible_take():
    fen = FEN.Fen('8/8/8/4P3/3PrP2/4P3/8/8 b KQkq - 0 1')
    moves = GAME.get_available_moves('ROOK', 36, fen)
    assert len(moves) is 4
    for move in moves:
        assert fen[move].isupper()


def test_blocked_with_possible_take():
    fen = FEN.Fen('8/8/8/4P3/2PprpP1/4P3/8/8 b KQkq - 0 1')
    moves = GAME.get_available_moves('ROOK', 36, fen)
    assert len(moves) is 2
    for move in moves:
        assert fen[move].isupper()


def test_blocked_take():
    assert len(GAME.get_available_moves('ROOK', 36, FEN.Fen('8/8/4P3/4p3/2PprpP1/4p3/4P3/8 b KQkq - 0 1'))) is 0
