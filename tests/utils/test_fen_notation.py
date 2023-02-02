import pytest
from utils import FEN_notation as FEN


@pytest.mark.parametrize("index,expected", [
    (0, 'r'),
    (1, 'n'),
    (2, 'b'),
    (3, 'q'),
    (4, 'k'),
    (5, 'b'),
    (6, 'n'),
    (7, 'r'),
])
def test_fen_getitem(index, expected):
    fen = FEN.Fen()
    assert fen[index] is expected


@pytest.mark.parametrize("index", [64, -1])
def test_invalid_fen_getitem(index):
    fen = FEN.Fen()
    with pytest.raises(IndexError):
        fen[index]


@pytest.mark.parametrize("anc,expected", [
    ('1a', 56),
    ('1b', 57),
    ('1c', 58),
    ('1d', 59),
    ('1e', 60),
    ('1f', 61),
    ('1g', 62),
    ('1h', 63)
])
def test_get_index_from_anc(anc, expected):
    assert FEN.get_index_from_anc(anc) is expected


@pytest.mark.parametrize("anc", ['-8a', 'b8', '88', '9d', '8x'])
def test_invalid_get_index_from_anc(anc):
    with pytest.raises(IndexError):
        FEN.get_index_from_anc(anc)


@pytest.mark.parametrize("fen_notation,expected", [
    ("r1b1k1nr/p2p1pNp/n2B4/1p1NP2P/6P1/3P1Q2/P1P1K3/q5b1",
     ['r', '@', 'b', '@', 'k', '@', 'n', 'r', 'p', '@', '@', 'p', '@', 'p', 'N', 'p', 'n', '@', '@', 'B', '@', '@', '@',
      '@', '@', 'p', '@', 'N', 'P', '@', '@', 'P', '@', '@', '@', '@', '@', '@', 'P', '@', '@', '@', '@', 'P', '@', 'Q',
      '@', '@', 'P', '@', 'P', '@', 'K', '@', '@', '@', 'q', '@', '@', '@', '@', '@', 'b', '@']),
    ("8/5k2/3p4/1p1Pp2p/pP2Pp1P/P4P1K/8/8",
     ['@', '@', '@', '@', '@', '@', '@', '@', '@', '@', '@', '@', '@', 'k', '@', '@', '@', '@', '@', 'p', '@', '@', '@',
      '@', '@', 'p', '@', 'P', 'p', '@', '@', 'p', 'p', 'P', '@', '@', 'P', 'p', '@', 'P', 'P', '@', '@', '@', '@', 'P',
      '@', 'K', '@', '@', '@', '@', '@', '@', '@', '@', '@', '@', '@', '@', '@', '@', '@', '@']),
    ("rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R",
     ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r', 'p', 'p', '@', 'p', 'p', 'p', 'p', 'p', '@', '@', '@', '@', '@', '@', '@',
      '@', '@', '@', 'p', '@', '@', '@', '@', '@', '@', '@', '@', '@', 'P', '@', '@', '@', '@', '@', '@', '@', '@', 'N',
      '@', '@', 'P', 'P', 'P', 'P', '@', 'P', 'P', 'P', 'R', 'N', 'B', 'Q', 'K', 'B', '@', 'R'])
])
def test_expand_fen(fen_notation, expected):
    assert FEN.Fen(fen_notation).expanded == expected
    assert len(FEN.Fen(fen_notation).expanded) == 64


@pytest.mark.parametrize("expanded_fen,expected", [
    (['r', '@', 'b', '@', 'k', '@', 'n', 'r', 'p', '@', '@', 'p', '@', 'p', 'N', 'p', 'n', '@', '@', 'B', '@', '@', '@',
      '@', '@', 'p', '@', 'N', 'P', '@', '@', 'P', '@', '@', '@', '@', '@', '@', 'P', '@', '@', '@', '@', 'P', '@', 'Q',
      '@', '@', 'P', '@', 'P', '@', 'K', '@', '@', '@', 'q', '@', '@', '@', '@', '@', 'b', '@'],
     "r1b1k1nr/p11p1pNp/n11B1111/1p1NP11P/111111P1/111P1Q11/P1P1K111/q11111b1"),
    (['@', '@', '@', '@', '@', '@', '@', '@', '@', '@', '@', '@', '@', 'k', '@', '@', '@', '@', '@', 'p', '@', '@', '@',
      '@', '@', 'p', '@', 'P', 'p', '@', '@', 'p', 'p', 'P', '@', '@', 'P', 'p', '@', 'P', 'P', '@', '@', '@', '@', 'P',
      '@', 'K', '@', '@', '@', '@', '@', '@', '@', '@', '@', '@', '@', '@', '@', '@', '@', '@'],
     "11111111/11111k11/111p1111/1p1Pp11p/pP11Pp1P/P1111P1K/11111111/11111111"),
    (['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r', 'p', 'p', '@', 'p', 'p', 'p', 'p', 'p', '@', '@', '@', '@', '@', '@', '@',
      '@', '@', '@', 'p', '@', '@', '@', '@', '@', '@', '@', '@', '@', 'P', '@', '@', '@', '@', '@', '@', '@', '@', 'N',
      '@', '@', 'P', 'P', 'P', 'P', '@', 'P', 'P', 'P', 'R', 'N', 'B', 'Q', 'K', 'B', '@', 'R'],
     "rnbqkbnr/pp1ppppp/11111111/11p11111/1111P111/11111N11/PPPP1PPP/RNBQKB1R")
])
def test_pack_fen(expanded_fen, expected):
    fen = FEN.Fen()
    fen.expanded = expanded_fen
    packed = fen.get_packed()
    assert packed == expected
    assert len(fen.get_expanded()) == 64


@pytest.mark.parametrize("fen_notation", [
    '8/8/8/8/8/8/8/8',
    'rnb1kbnr/pppp1ppp/4p3/8/6Pq/5P2/PPPPP2P/RNBQKBNR',
    '8/8/8/3PpP2/3pKp2/3PpP2/8/8',
    '8/8/8/5p2/4b3/3p1p2/2P3P1/8',
    '8/5pp1/2p2P2/2P5/7p/1P2p3/2P1PP1P/8',
    'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'
])
def test_fen_validation(fen_notation: str):
    assert FEN.validate_fen_notation(fen_notation)


@pytest.mark.parametrize("fen_notation", [
    '8/8/8/8/8/8/8/9',
    'rnb1kbnr/pppp1ppp/4p3/8/6Pq/5P2/PPPPP2P/RNBQKBLR',
    '8/8/8/3PpP2/3pKp2/3P0pP2/8/8',
    '8/8/8/5p2/4b3/3p1p2/2P3PP1/8',
])
def test_fail_fen_validation(fen_notation: str):
    with pytest.raises(Exception):
        assert FEN.validate_fen_notation(fen_notation)


@pytest.mark.parametrize("fen_notation", [
    '8/8/8/8/8/8/8/8',
    'rnb1kbnr/pppp1ppp/4p3/8/6Pq/5P2/PPPPP2P/RNBQKBNR',
    '8/8/8/3PpP2/3pKp2/3PpP2/8/8',
    '8/8/8/5p2/4b3/3p1p2/2P3P1/8',
    '8/5pp1/2p2P2/2P5/7p/1P2p3/2P1PP1P/8',
    'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'
])
def test_fen_repr(fen_notation):
    assert len(FEN.Fen(fen_notation).__repr__()) is 71
    assert len(FEN.Fen(fen_notation).__repr__().split('\n')) is 8


def test_fen_setitem():
    fen = FEN.Fen('8/8/8/8/8/8/8/8')
    fen[10] = 'k'
    assert fen[10] is 'k'
    fen[10] = fen[0]
    assert fen[10] is FEN.FenChars.BLANK_PIECE.value
    assert fen[0] is FEN.FenChars.BLANK_PIECE.value
