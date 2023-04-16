import pytest

from chess.notation.forsyth_edwards_notation import Fen, FenChars
from chess.movement.piece_movement import get_available_moves
import chess.movement.validate_move as validate_move


def test_check():
    assert validate_move.is_check(Fen('8/8/8/3PpP2/3pkp2/3PpP2/8/8 b KQkq - 0 1'))


def test_not_in_check():
    assert not validate_move.is_check(Fen())


def test_moving_into_check():
    assert len(get_available_moves(36, Fen('7k/8/8/3PpP2/3pKp2/3PpP2/8/8 w - - 0 1'))) is 1
    assert len(get_available_moves(44, Fen('7k/8/8/6b1/8/4P3/3K4/8 w - - 0 1'))) is 0


@pytest.mark.parametrize("fen,piece_fen_val", [
    # get out with take
    (Fen('8/8/8/8/2B1P3/3P1N2/PPP2qPP/RNBQK2R w KQkq - 0 1'), 'K'),
    # get out with block
    (Fen('2Q4k/6pp/5r1q/8/8/8/8/8 b KQkq - 0 1'), 'r'),
    # get out with move
    (Fen('2Q3k1/6pp/7q/8/8/8/8/8 b KQkq - 0 1'), 'k')
])
def test_get_out_check(fen: Fen, piece_fen_val: str):
    assert validate_move.is_check(fen)
    for index, fen_val in enumerate(fen.expanded):
        if fen_val is FenChars.BLANK_PIECE: continue
        if fen_val.islower() if fen.is_white_turn() else fen_val.isupper(): continue

        moves = get_available_moves(index, fen)

        if fen_val == piece_fen_val:
            assert len(moves) == 1
        else:
            assert len(moves) == 0
