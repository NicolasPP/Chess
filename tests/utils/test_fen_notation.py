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
    (10, 'p'),
    (11, 'p'),
    (12, 'p'),
    (13, 'p'),
    (16, '@'),
    (17, '@'),
    (18, '@'),
    (19, '@'),
    (48, 'P'),
    (49, 'P'),
    (50, 'P'),
    (51, 'P'),
    (56, 'R'),
    (57, 'N'),
    (58, 'B'),
    (59, 'Q'),
    (60, 'K'),
    (61, 'B'),
    (62, 'N'),
    (63, 'R')
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
    ('8a', 0),
    ('8b', 1),
    ('8c', 2),
    ('8d', 3),
    ('8e', 4),
    ('8f', 5),
    ('8g', 6),
    ('8h', 7),
    ('7a', 8),
    ('7b', 9),
    ('7c', 10),
    ('7d', 11),
    ('2e', 52),
    ('2f', 53),
    ('2g', 54),
    ('2h', 55),
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
