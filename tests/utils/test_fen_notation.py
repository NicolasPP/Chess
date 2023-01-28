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
def test_fen_invalid_getitem(index):
	fen = FEN.Fen()
	with pytest.raises(IndexError):
		fen[index]