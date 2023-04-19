import sys
import time

import pygame
import click

from chess.game.chess_match import Match
from chess.chess_player import Player, process_command_local, State
from chess.board.side import Side
from chess.asset.chess_assets import PieceSetAssets, Themes, ChessTheme, PieceSetAsset
from chess.timer.timer_config import DefaultConfigs, TimerConfig
from chess.game.game_surface import GameSurface
from chess.chess_init import init_chess

prev_time = time.time()
delta_time: float = 0


def set_delta_time() -> None:
    global prev_time, delta_time
    now = time.time()
    delta_time = now - prev_time
    prev_time = now


def main_loop(theme: ChessTheme, scale: float, piece_set: PieceSetAsset) -> None:
    done = False
    is_white = True
    init_chess(theme, piece_set, scale)
    center: pygame.rect.Rect = GameSurface.get().get_rect(center=pygame.display.get_surface().get_rect().center)
    match = Match(DefaultConfigs.BLITZ_5)
    white_player: Player = Player.get_player_local(Side.WHITE, match, center)
    black_player: Player = Player.get_player_local(Side.BLACK, match, center)

    while not done:

        set_delta_time()

        current_player = white_player if is_white else black_player

        for event in pygame.event.get():
            keys = pygame.key.get_pressed()
            if event.type == pygame.QUIT: done = True
            if event.type == pygame.KEYDOWN:
                if keys[pygame.K_SPACE] and current_player.state is not State.PICKING_PROMOTION:
                    is_white = not is_white
                    white_player.set_require_render(True)
                    black_player.set_require_render(True)
            current_player.parse_input(event, match.fen, local=True)

        match.process_local_move()

        process_command_local(match.fen, white_player, black_player)

        white_player.update(delta_time, local=True)
        black_player.update(delta_time, local=True)
        current_player.render()

        pygame.display.get_surface().blit(GameSurface.get(), center)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


@click.command()
@click.option('--scale', default=3.5, help='size of chess game, lower than 3.5 will cause the fonts to be unclear')
@click.option('--theme_id', default=-1, help='game theme, possible ids (1 - 4) and (-1 for random)')
@click.option('--pieces_asset', default='RANDOM', help='piece assets, possible names SMALL, LARGE, RANDOM')
def start_local_game(scale: float, theme_id: int, pieces_asset: str) -> None:
    main_loop(Themes.get_theme(theme_id), scale, PieceSetAssets.get_asset(pieces_asset))


if __name__ == "__main__":
    start_local_game()
