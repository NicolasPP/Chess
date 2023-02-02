import pytest

import chess.chess_data as CHESS
import chess.game as GAME
import utils.FEN_notation as FEN


def test_check():
    assert len(GAME.get_available_moves('KING', 36, FEN.Fen('8/8/8/3PpP2/3pKp2/3PpP2/8/8'), True)) is 1


def test_moving_into_check():
    assert len(GAME.get_available_moves('PAWN', 44, FEN.Fen('8/8/8/6b1/8/4P3/3K4/8'), True)) is 0


@pytest.mark.parametrize("fen,is_white_turn,piece_fen_val", [
    # get out with take
    (FEN.Fen('8/8/8/8/2B1P3/3P1N2/PPP2qPP/RNBQK2R'), True, 'K'),
    # get out with block
    (FEN.Fen('2Q4k/6pp/5r1q/8/8/8/8/8'), False, 'r'),
    # get out with move
    (FEN.Fen('2Q3k1/6pp/7q/8/8/8/8/8'), False, 'k')
])
def test_get_out_check(fen: FEN.Fen, is_white_turn: bool, piece_fen_val: str):
    for index, fen_val in enumerate(fen.expanded):
        if fen_val is FEN.FenChars.BLANK_PIECE.value: continue
        if fen_val.islower() if is_white_turn else fen_val.isupper(): continue
        piece_name = CHESS.get_name_from_fen(fen_val)
        moves = GAME.get_available_moves(piece_name, index, fen, is_white_turn)

        if fen_val == piece_fen_val:
            assert len(moves) is 1
        else:
            assert len(moves) is 0
