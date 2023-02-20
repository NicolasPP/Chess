import pytest

import chess.game as GAME
import utils.Forsyth_Edwards_notation as FEN


@pytest.mark.parametrize("fen", [
    FEN.Fen('rnb1kbnr/pppp1ppp/4p3/8/6Pq/5P2/PPPPP2P/RNBQKBNR b KQkq - 0 1'),
    FEN.Fen('3rkbnr/1p1bp3/1q1p3p/p5pQ/8/8/8/8 w KQkq - 0 1'),
    FEN.Fen('R6k/R7/8/8/8/8/8/5K2 w KQkq - 0 1'),
    FEN.Fen('r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/8/8 w KQkq - 0 1'),
    FEN.Fen('6Rk/8/5N2/8/8/8/8/8 w KQkq - 0 1')
])
def test_checkmate(fen: FEN.Fen):
    assert GAME.is_opponent_in_checkmate(fen)