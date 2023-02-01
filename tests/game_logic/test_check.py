import pytest

import utils.FEN_notation as FEN
import chess.game as GAME


def test_check():
    assert len(GAME.get_available_moves('KING', 36, FEN.Fen('8/8/8/3PpP2/3pKp2/3PpP2/8/8'), True)) is 1
