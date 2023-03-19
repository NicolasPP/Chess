import pytest

from utils.algebraic_notation import get_an_from_index, get_index_from_an


@pytest.mark.parametrize("index,expected", [
    (56, 'a1'),
    (57, 'b1'),
    (58, 'c1'),
    (59, 'd1'),
    (60, 'e1'),
    (61, 'f1'),
    (62, 'g1'),
    (63, 'h1')
])
def test_get_an_from_index(index: int, expected: str):
    assert get_an_from_index(index).data.coordinates == expected


@pytest.mark.parametrize("index", [-1, 65])
def test_invalid_get_an_from_index(index: int):
    with pytest.raises(IndexError):
        get_an_from_index(index)


@pytest.mark.parametrize("an,expected", [
    ('a1', 56),
    ('b1', 57),
    ('c1', 58),
    ('d1', 59),
    ('e1', 60),
    ('f1', 61),
    ('g1', 62),
    ('h1', 63)
])
def test_get_index_from_anc(an, expected):
    assert get_index_from_an(*an) is expected


@pytest.mark.parametrize("file,rank", [('a', '-8'), ('8', 'b'), ('8', '8'), ('9', 'd'), ('8', 'x')])
def test_validate_file_and_rank(file: str, rank: str):
    with pytest.raises(Exception):
        get_index_from_an(file, rank)
