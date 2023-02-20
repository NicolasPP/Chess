import pytest

import utils.Forsyth_Edwards_notation as FEN


@pytest.fixture(scope="session")
def pawn_test_fen() -> FEN.Fen: return FEN.Fen("8/5pp1/2p2P2/2P5/7p/1P2p3/2P1PP1P/8 w KQkq - 0 1")
