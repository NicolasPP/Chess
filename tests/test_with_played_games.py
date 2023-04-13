import pytest

from chess.movement.validate_move import is_move_valid
from chess.notation.forsyth_edwards_notation import Fen
import chess.notation.portable_game_notation as game_notation


def get_games() -> list[game_notation.Game]:
    magnus = game_notation.PortableGameNotation('game_data/magnus_carlsen_latest_games.pgn')
    hikaru = game_notation.PortableGameNotation('game_data/hikaru_nakamura_latest_games.pgn')
    return magnus.games + hikaru.games


@pytest.mark.played_games
@pytest.mark.parametrize("game", get_games())
def test_against_played_games(game: game_notation.Game):
    fen = Fen()
    for from_an, dest_an, target_fen in game_notation.get_an_from_pgn_game(game):
        assert is_move_valid(from_an.data.index, dest_an.data.index, fen)
        fen.make_move(from_an.data.index, dest_an.data.index, target_fen)
