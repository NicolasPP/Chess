import pytest

import chess.game as GAME
import utils.Forsyth_Edwards_notation as FEN
import utils.portable_game_notation as PGN


def get_games() -> list[PGN.Game]:
    magnus = PGN.PortableGameNotation('game_data/magnus_carlsen_latest_games.pgn')
    hikaru = PGN.PortableGameNotation('game_data/hikaru_nakamura_latest_games.pgn')
    return magnus.games + hikaru.games


@pytest.mark.integrated
@pytest.mark.parametrize("game", get_games())
def test_against_played_games(game: PGN.Game):
    fen = FEN.Fen()
    for from_an, dest_an, target_fen in PGN.get_an_from_pgn_game(game):
        assert GAME.is_move_valid(from_an.data.index, dest_an.data.index, fen)
        fen.make_move(from_an.data.index, dest_an.data.index, target_fen)
