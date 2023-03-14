import pytest

from utils.Forsyth_Edwards_notation import Fen, FenChars
import chess.validate_move as validate_move
import chess.piece as chess_piece

chess_piece.Pieces.load_pieces_info()


def test_check(load_pieces_info):
    assert validate_move.is_opponent_in_check(Fen('8/8/8/3PpP2/3pkp2/3PpP2/8/8 w KQkq - 0 1'))


def test_not_in_check(load_pieces_info):
    assert not validate_move.is_opponent_in_check(Fen())


def test_moving_into_check(load_pieces_info):
    assert len(chess_piece.get_available_moves('K', 36, Fen('7k/8/8/3PpP2/3pKp2/3PpP2/8/8 w - - 0 1'))) is 1
    assert len(chess_piece.get_available_moves('P', 44, Fen('7k/8/8/6b1/8/4P3/3K4/8 w - - 0 1'))) is 0


@pytest.mark.parametrize("fen,piece_fen_val", [
    # get out with take
    (Fen('8/8/8/8/2B1P3/3P1N2/PPP2qPP/RNBQK2R b KQkq - 0 1'), 'K'),
    # get out with block
    (Fen('2Q4k/6pp/5r1q/8/8/8/8/8 w KQkq - 0 1'), 'r'),
    # get out with move
    (Fen('2Q3k1/6pp/7q/8/8/8/8/8 w KQkq - 0 1'), 'k')
])
def test_get_out_check(load_pieces_info, fen: Fen, piece_fen_val: str):
    assert validate_move.is_opponent_in_check(fen)
    for index, fen_val in enumerate(fen.expanded):
        if fen_val is FenChars.BLANK_PIECE.value: continue
        if fen_val.isupper() if fen.is_white_turn() else fen_val.islower(): continue

        moves = chess_piece.get_available_moves(fen_val, index, fen, not fen.is_white_turn())

        if fen_val == piece_fen_val:
            assert len(moves) == 1
        else:
            assert len(moves) == 0
