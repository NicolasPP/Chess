from chess.notation.algebraic_notation import AlgebraicNotation
from chess.notation.portable_game_notation import generate_move_text
from chess.notation.forsyth_edwards_notation import Fen


class PlayedMovesGui:
    def __init__(self) -> None:
        self.played_moves: list[str] = []

    def add_played_move(self, from_index: int, dest_index: int, fen: Fen, target_fen: str) -> None:
        from_an = AlgebraicNotation.get_an_from_index(from_index)
        dest_an = AlgebraicNotation.get_an_from_index(dest_index)
        move = generate_move_text(fen, from_an, dest_an, target_fen)
        print(move)
        self.played_moves.append(move)
