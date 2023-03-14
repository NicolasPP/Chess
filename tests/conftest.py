import pytest

from chess.piece import Pieces


@pytest.fixture(scope="session")
def load_pieces_info() -> None:
    Pieces.load_pieces_info()
