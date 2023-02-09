import pytest

import utils.portable_game_notation as PGN
import utils.FEN_notation as FEN


def get_games() -> list[PGN.Game]:
    magnus = PGN.PortableGameNotation('game_data/magnus_carlsen_latest_games.pgn')
    hikaru = PGN.PortableGameNotation('game_data/hikaru_nakamura_latest_games.pgn')
    return magnus.games + hikaru.games


@pytest.mark.xfail
@pytest.mark.parametrize("game", get_games())
def test_against_played_games(game: PGN.Game):
    fen = FEN.Fen()
    pass