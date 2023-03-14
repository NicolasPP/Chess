from src.chess.piece import Pieces


def pytest_sessionstart(session):
    Pieces.load_pieces_info()
