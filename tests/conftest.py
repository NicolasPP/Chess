from chess.piece_movement import PieceMovement


def pytest_sessionstart(session):
    PieceMovement.load()
