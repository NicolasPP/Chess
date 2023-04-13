import random
import sys
import time

import pygame

from chess.match import Match
from chess.player import Player, process_command_local, State
from chess.piece_movement import Side
from chess.asset.chess_assets import PieceSetAssets, Themes
from chess.chess_timer import DefaultConfigs
from chess.game_surface import GameSurface
from chess.chess_init import init_chess

from config import *

done = False
prev_time = time.time()
delta_time: float = 0
theme = random.choice((Themes.PLAIN1, Themes.PLAIN2, Themes.PLAIN3, Themes.PLAIN4))
init_chess(theme, SCALE)

match = Match(DefaultConfigs.BLITZ_5)
center = GameSurface.get().get_rect(center=pygame.display.get_surface().get_rect().center)

white_player = Player(
    side=Side.WHITE,
    piece_set=random.choice([PieceSetAssets.NORMAL16x32, PieceSetAssets.NORMAL16x16]),
    scale=SCALE,
    time_left=match.timer_config.time,
    game_offset=center
)

black_player = Player(
    side=Side.BLACK,
    piece_set=random.choice([PieceSetAssets.NORMAL16x32, PieceSetAssets.NORMAL16x16]),
    scale=SCALE,
    time_left=match.timer_config.time,
    game_offset=center
)

white_player.update_turn(match.fen)
black_player.update_turn(match.fen)

white_player.update_pieces_location(match.fen)
black_player.update_pieces_location(match.fen)


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


is_white = True
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
