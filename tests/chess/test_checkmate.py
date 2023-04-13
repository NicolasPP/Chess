import pytest

import chess.movement.validate_move as validate_move
from chess.notation.forsyth_edwards_notation import Fen


@pytest.mark.parametrize("fen", [
    Fen('rnb1kbnr/pppp1ppp/4p3/8/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 0 1'),
    Fen('3rkbnr/1p1bp3/1q1p3p/p5pQ/8/8/8/8 b KQkq - 0 1'),
    Fen('R6k/R7/8/8/8/8/8/5K2 b KQkq - 0 1'),
    Fen('r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/8/8 b KQkq - 0 1'),
    Fen('6Rk/8/5N2/8/8/8/8/8 b KQkq - 0 1')
])
def test_checkmate(fen: Fen):
    assert validate_move.is_checkmate(fen)


def test_false_checkmate():
    assert validate_move.is_checkmate(Fen("k7/2Q5/8/8/8/8/8/7K w - - 0 1")) is False
