import utils.FEN_notation as FEN
import chess.game as GAME

def test_checkmate():
    assert len(GAME.get_available_moves('KING', 60, FEN.Fen('rnb1kbnr/pppp1ppp/4p3/8/6Pq/5P2/PPPPP2P/RNBQKBNR'), True)) is 0
