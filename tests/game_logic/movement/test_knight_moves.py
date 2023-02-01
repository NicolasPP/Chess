import utils.FEN_notation as FEN
import chess.game as GAME


def test_base_moves():
    assert len(GAME.get_available_moves('KNIGHT', 36, FEN.Fen('8/8/8/8/8/8/8/8'), True)) is 8


def test_default_fen_moves():
    fen = FEN.Fen()
    assert len(GAME.get_available_moves('KNIGHT', 1, fen, False)) == 2
    assert len(GAME.get_available_moves('KNIGHT', 5, fen, False)) == 2
    assert len(GAME.get_available_moves('KNIGHT', 62, fen, True)) == 2
    assert len(GAME.get_available_moves('KNIGHT', 57, fen, True)) == 2


def test_fully_blocked():
    assert len(GAME.get_available_moves('KNIGHT', 36, FEN.Fen('8/8/3p1p2/2p3p1/4k3/2p3p1/3p1p2/8'), False)) == 0


def test_jump_over_piece():
    assert(len(GAME.get_available_moves('KNIGHT', 36, FEN.Fen('8/8/3P1P2/2PpppP1/3pkp2/2PpppP1/3P1P2/8'), False)) == 4)

def test_possible_take():
    is_white_turn = False
    from_index = 36
    fen = FEN.Fen('8/8/3P1P2/2P3P1/4k3/2P3P1/3P1P2/8')
    moves = GAME.get_available_moves('KNIGHT', from_index, fen, is_white_turn)
    assert len(moves) == 4
    for move in moves:
        assert fen.expanded[move].isupper()
