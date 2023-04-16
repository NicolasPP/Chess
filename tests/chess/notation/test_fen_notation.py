import pytest
import chess.notation.forsyth_edwards_notation as notation


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
    fen = notation.Fen()
    assert fen[index] is expected


@pytest.mark.parametrize("index", [64, -1])
def test_invalid_fen_getitem(index):
    fen = notation.Fen()
    with pytest.raises(IndexError):
        fen[index]


@pytest.mark.parametrize("fen_notation,expected", [
    ("r1b1k1nr/p2p1pNp/n2B4/1p1NP2P/6P1/3P1Q2/P1P1K3/q5b1 w KQkq - 0 1",
     ['r', '@', 'b', '@', 'k', '@', 'n', 'r', 'p', '@', '@', 'p', '@', 'p', 'N', 'p', 'n', '@', '@', 'B', '@', '@', '@',
      '@', '@', 'p', '@', 'N', 'P', '@', '@', 'P', '@', '@', '@', '@', '@', '@', 'P', '@', '@', '@', '@', 'P', '@', 'Q',
      '@', '@', 'P', '@', 'P', '@', 'K', '@', '@', '@', 'q', '@', '@', '@', '@', '@', 'b', '@']),
    ("8/5k2/3p4/1p1Pp2p/pP2Pp1P/P4P1K/8/8 w KQkq - 0 1",
     ['@', '@', '@', '@', '@', '@', '@', '@', '@', '@', '@', '@', '@', 'k', '@', '@', '@', '@', '@', 'p', '@', '@', '@',
      '@', '@', 'p', '@', 'P', 'p', '@', '@', 'p', 'p', 'P', '@', '@', 'P', 'p', '@', 'P', 'P', '@', '@', '@', '@', 'P',
      '@', 'K', '@', '@', '@', '@', '@', '@', '@', '@', '@', '@', '@', '@', '@', '@', '@', '@']),
    ("rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 1",
     ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r', 'p', 'p', '@', 'p', 'p', 'p', 'p', 'p', '@', '@', '@', '@', '@', '@', '@',
      '@', '@', '@', 'p', '@', '@', '@', '@', '@', '@', '@', '@', '@', 'P', '@', '@', '@', '@', '@', '@', '@', '@', 'N',
      '@', '@', 'P', 'P', 'P', 'P', '@', 'P', 'P', 'P', 'R', 'N', 'B', 'Q', 'K', 'B', '@', 'R'])
])
def test_expand_fen(fen_notation, expected):
    assert notation.Fen(fen_notation).expanded == expected
    assert len(notation.Fen(fen_notation).expanded) == 64


@pytest.mark.parametrize("expanded_fen,expected", [
    (['r', '@', 'b', '@', 'k', '@', 'n', 'r', 'p', '@', '@', 'p', '@', 'p', 'N', 'p', 'n', '@', '@', 'B', '@', '@', '@',
      '@', '@', 'p', '@', 'N', 'P', '@', '@', 'P', '@', '@', '@', '@', '@', '@', 'P', '@', '@', '@', '@', 'P', '@', 'Q',
      '@', '@', 'P', '@', 'P', '@', 'K', '@', '@', '@', 'q', '@', '@', '@', '@', '@', 'b', '@'],
     "r1b1k1nr/p2p1pNp/n2B4/1p1NP2P/6P1/3P1Q2/P1P1K3/q5b1"),
    (['@', '@', '@', '@', '@', '@', '@', '@', '@', '@', '@', '@', '@', 'k', '@', '@', '@', '@', '@', 'p', '@', '@', '@',
      '@', '@', 'p', '@', 'P', 'p', '@', '@', 'p', 'p', 'P', '@', '@', 'P', 'p', '@', 'P', 'P', '@', '@', '@', '@', 'P',
      '@', 'K', '@', '@', '@', '@', '@', '@', '@', '@', '@', '@', '@', '@', '@', '@', '@', '@'],
     "8/5k2/3p4/1p1Pp2p/pP2Pp1P/P4P1K/8/8"),
    (['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r', 'p', 'p', '@', 'p', 'p', 'p', 'p', 'p', '@', '@', '@', '@', '@', '@', '@',
      '@', '@', '@', 'p', '@', '@', '@', '@', '@', '@', '@', '@', '@', 'P', '@', '@', '@', '@', '@', '@', '@', '@', 'N',
      '@', '@', 'P', 'P', 'P', 'P', '@', 'P', 'P', 'P', 'R', 'N', 'B', 'Q', 'K', 'B', '@', 'R'],
     "rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R")
])
def test_pack_fen(expanded_fen, expected):
    fen = notation.Fen()
    fen.expanded = expanded_fen
    packed = fen.get_packed()
    assert packed == expected
    assert len(fen.get_expanded()) == 64


@pytest.mark.parametrize("fen_notation", [
    '8/8/8/8/8/8/8/8 w KQkq - 0 1',
    'rnb1kbnr/pppp1ppp/4p3/8/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 0 1',
    '8/8/8/3PpP2/3pKp2/3PpP2/8/8 w KQkq - 0 1',
    '8/8/8/5p2/4b3/3p1p2/2P3P1/8 w KQkq - 0 1',
    '8/5pp1/2p2P2/2P5/7p/1P2p3/2P1PP1P/8 w KQkq - 0 1',
    'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
])
def test_fen_validation(fen_notation: str):
    assert notation.Fen(fen_notation)


@pytest.mark.parametrize("fen_notation", [
    '8/8/8/8/8/8/8/9 w KQkq - 0 1',
    'rnb1kbnr/pppp1ppp/4p3/8/6Pq/5P2/PPPPP2P/RNBQKBLR w KQkq - 0 1',
    '8/8/8/3PpP2/3pKp2/3P0pP2/8/8 w KQkq - 0 1',
    '8/8/8/5p2/4b3/3p1p2/2P3PP1/8 w KQkq - 0 1',
])
def test_fail_fen_validation(fen_notation: str):
    with pytest.raises(Exception):
        assert notation.Fen(fen_notation)


@pytest.mark.parametrize("fen_notation", [
    '8/8/8/8/8/8/8/8 w KQkq - 0 1',
    'rnb1kbnr/pppp1ppp/4p3/8/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 0 1',
    '8/8/8/3PpP2/3pKp2/3PpP2/8/8 w KQkq - 0 1',
    '8/8/8/5p2/4b3/3p1p2/2P3P1/8 w KQkq - 0 1',
    '8/5pp1/2p2P2/2P5/7p/1P2p3/2P1PP1P/8 w KQkq - 0 1',
    'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
])
def test_fen_repr(fen_notation):
    assert len(notation.Fen(fen_notation).__repr__()) is 71
    assert len(notation.Fen(fen_notation).__repr__().split('\n')) is 8


def test_fen_setitem():
    fen = notation.Fen('8/8/8/8/8/8/8/8 w KQkq - 0 1')
    fen[10] = 'k'
    assert fen[10] is 'k'
    fen[10] = fen[0]
    assert fen[10] is notation.FenChars.BLANK_PIECE
    assert fen[0] is notation.FenChars.BLANK_PIECE


def test_fen_notation():
    fen = notation.Fen()
    fen.notation = '8/8/8/8/8/8/8/8 w KQkq - 0 1'
    assert fen.notation == notation.encode_fen_data(fen.data)
    del fen.notation


def test_fen_str():
    fen = notation.Fen()
    assert str(fen) == 'fen : ' + fen.data.piece_placement + '\n' + fen.__repr__()


@pytest.mark.parametrize("fen_notation,expected", [
    ("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
     notation.FenData("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR", "w", "KQkq", "-", "0", "1")),
    ("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR b KQkq - 3 1",
     notation.FenData("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR", "b", "KQkq", "-", "3", "1")),
])
def test_decode_fen_notation(fen_notation, expected):
    assert notation.decode_fen_notation(fen_notation) == expected


@pytest.mark.parametrize("fen_notation", [
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1 -",
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0"
])
def test_fail_decode_fen_notation(fen_notation):
    with pytest.raises(Exception):
        notation.decode_fen_notation(fen_notation)


@pytest.mark.parametrize("fen_data,expected", [
    (notation.FenData("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR", "w", "KQkq", "-", "0", "1"),
     "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"),
    (notation.FenData("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR", "b", "KQkq", "-", "3", "1"),
     "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR b KQkq - 3 1",),
])
def test_encode_fen_notation(fen_data: notation.FenData, expected: str):
    assert notation.encode_fen_data(fen_data) == expected


def test_get_next_active_color():
    f = notation.Fen()
    assert f.data.active_color == 'w'
    f.make_move(30, 33, f[30])
    assert f.data.active_color == 'b'
    f.make_move(33, 30, f[33])
    assert f.data.active_color == 'w'
    f.make_move(30, 33, f[30])
    assert f.data.active_color == 'b'


def test_get_full_move_number():
    f = notation.Fen()
    assert f.data.full_move_number == '1'
    f.make_move(30, 33, f[30])
    assert f.data.full_move_number == '1'
    f.make_move(33, 30, f[33])
    assert f.data.full_move_number == '2'


def test_get_half_move_number():
    f = notation.Fen()
    assert f.data.half_move_clock == '0'
    f.make_move(1, 16, f[1])
    assert f.data.half_move_clock == '1'
    f.make_move(8, 16, f[8])
    assert f.data.half_move_clock == '0'


def test_get_en_passant_rights():
    f = notation.Fen("8/1ppppppp/8/p7/8/8/PPPPPPPP/8 b KQkq - 0 1")
    assert f.get_en_passant_rights('p', 8, 24) == 'a6'
    f = notation.Fen("8/1ppppppp/8/p7/P7/8/1PPPPPPP/8 w KQkq - 0 1")
    assert f.get_en_passant_rights('P', 48, 32) == 'a3'


def test_get_castling_rights():
    f = notation.Fen("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    assert f.get_castling_rights('K', 60) == 'kq'
    f = notation.Fen("r3k2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1")
    assert f.get_castling_rights('k', 4) == 'KQ'
    f = notation.Fen("r3k2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1")
    assert f.get_castling_rights('r', 0) == 'KQk'
    f = notation.Fen('r3k2r/8/8/8/8/8/7R/R3K3 w KQkq - 1 2')
    assert f.get_castling_rights('R', 63) == 'Qkq'


def test_make_castle_move():
    f = notation.Fen("r3k2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1")
    f.make_move(4, 0, f[4])
    assert f[2] == 'k'
    assert f[3] == 'r'
    f.make_move(60, 63, f[60])
    assert f[62] == 'K'
    assert f[61] == 'R'


@pytest.mark.parametrize("full_move_number", ["k", "-1"])
def test_validate_fen_full_move_number(full_move_number: str):
    with pytest.raises(Exception):
        notation.validate_fen_full_move_number(full_move_number)


@pytest.mark.parametrize("active_color", ["h", "1", "*"])
def test_validate_fen_active_color(active_color: str):
    with pytest.raises(Exception):
        notation.validate_fen_active_color(active_color)


@pytest.mark.parametrize("half_move_clock", ["k", "-1", "101"])
def test_validate_fen_half_move_clock(half_move_clock: str):
    with pytest.raises(Exception):
        notation.validate_fen_half_move_clock(half_move_clock)


@pytest.mark.parametrize("en_passant_rights", ["10h", "a"])
def test_validate_fen_en_passant_rights(en_passant_rights: str):
    with pytest.raises(Exception):
        notation.validate_fen_half_move_clock(en_passant_rights)


@pytest.mark.parametrize("castling_rights", ["QKqkk", "", "opsd"])
def test_validate_fen_castling_rights(castling_rights: str):
    with pytest.raises(Exception):
        notation.validate_fen_castling_rights(castling_rights)
