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

@pytest.mark.parametrize("ANC,expected", [
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
def test_get_index_from_ANC(ANC, expected):
	assert FEN.get_index_from_ANC(ANC) is expected

@pytest.mark.parametrize("ANC", ['-8a','b8','88','9d', '8x'])
def test_invalid_get_index_from_ANC(ANC):
	with pytest.raises(IndexError):
		FEN.get_index_from_ANC(ANC)