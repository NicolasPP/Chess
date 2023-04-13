import random
import sys
import time

import pygame
import click

from chess.match import Match
from chess.player import Player, process_command_local, State
from chess.piece_movement import Side
from chess.asset.chess_assets import PieceSetAssets, Themes, ChessTheme
from chess.chess_timer import DefaultConfigs, TimerConfig
from chess.game_surface import GameSurface
from chess.chess_init import init_chess

prev_time = time.time()
delta_time: float = 0


def get_player(side: Side, match: Match, game_offset: pygame.rect.Rect) -> Player:
    player = Player(
        side=side,
        piece_set=random.choice([PieceSetAssets.NORMAL16x32, PieceSetAssets.NORMAL16x16]),
        time_left=match.timer_config.time,
        game_offset=game_offset
    )
    player.update_turn(match.fen)
    player.update_pieces_location(match.fen)
    return player


def get_match(timer_config: TimerConfig) -> Match:
    return Match(timer_config)


def set_delta_time() -> None:
    global prev_time, delta_time
    now = time.time()
    delta_time = now - prev_time
    prev_time = now


def update_window_caption(*players: Player) -> None:
    for player in players:
        if player.game_over:
            pygame.display.set_caption('GAME OVER')
            return
        if not player.turn: continue
        pygame.display.set_caption(f"{player.side.name}s TURN")
        return


def main_loop(theme: ChessTheme, scale: float) -> None:
    done = False
    is_white = True
    init_chess(theme, scale)
    match = get_match(DefaultConfigs.BLITZ_5)
    center: pygame.rect.Rect = GameSurface.get().get_rect(center=pygame.display.get_surface().get_rect().center)
    white_player: Player = get_player(Side.WHITE, match, center)
    black_player: Player = get_player(Side.BLACK, match, center)

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

        update_window_caption(white_player, black_player)

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
@click.option('--theme_id', default=1, help='game theme, possible ids (1 - 4) and (-1 for random theme)')
def start_local_game(scale: float, theme_id: int) -> None:
    main_loop(Themes.get_theme(theme_id), scale)


if __name__ == "__main__":
    start_local_game()
