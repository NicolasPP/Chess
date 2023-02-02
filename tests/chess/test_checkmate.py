import pytest

import chess.chess_data as CHESS
import chess.game as GAME
import utils.FEN_notation as FEN


@pytest.mark.parametrize("fen,is_white_turn", [
    (FEN.Fen('rnb1kbnr/pppp1ppp/4p3/8/6Pq/5P2/PPPPP2P/RNBQKBNR'), True),
    (FEN.Fen('3rkbnr/1p1bp3/1q1p3p/p5pQ/8/8/8/8'), False),
    (FEN.Fen('R6k/R7/8/8/8/8/8/8'), False),
    (FEN.Fen('r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/8/8'), False),
    (FEN.Fen('6Rk/8/5N2/8/8/8/8/8'), False)
])
def test_checkmate(fen: FEN.Fen, is_white_turn: bool):
    for index, fen_val in enumerate(fen.expanded):
        if fen_val is FEN.FenChars.BLANK_PIECE.value: continue
        if fen_val.islower() if is_white_turn else fen_val.isupper(): continue
        piece_name = CHESS.get_name_from_fen(fen_val)
        assert len(GAME.get_available_moves(piece_name, index, fen, is_white_turn)) is 0
