import pytest

import utils.FEN_notation as FEN
import chess.game as GAME


def test_base_moves():
    assert len(GAME.get_available_moves('KNIGHT', 36, FEN.Fen('8/8/8/8/8/8/8/8 w KQkq - 0 1'))) is 8


@pytest.mark.parametrize("from_index,is_white_turn", [(1, False), (5, False), (62, True), (57, True)])
def test_default_fen(from_index: int, is_white_turn: bool):
    fen = FEN.Fen()
    if not is_white_turn: fen.data.active_color = fen.get_next_active_color()
    assert len(GAME.get_available_moves('KNIGHT', from_index, fen)) == 2


def test_fully_blocked():
    assert len(GAME.get_available_moves('KNIGHT', 36, FEN.Fen('8/8/3p1p2/2p3p1/4k3/2p3p1/3p1p2/8 b KQkq - 0 1'))) == 0


def test_jump_over_piece():
    assert(len(GAME.get_available_moves('KNIGHT', 36, FEN.Fen('8/8/3P1P2/2PpppP1/3pkp2/2PpppP1/3P1P2/8 b KQkq - 0 1'))) == 4)


def test_possible_take():
    fen = FEN.Fen('8/8/3P1P2/2P3P1/4k3/2P3P1/3P1P2/8 b KQkq - 0 1')
    moves = GAME.get_available_moves('KNIGHT', 36, fen)
    assert len(moves) == 4
    for move in moves:
        assert fen[move].isupper()
