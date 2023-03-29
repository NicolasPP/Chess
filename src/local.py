import random
import sys
import time

import pygame

from chess.match import Match
from chess.player import Player, parse_command_local, STATE
from chess.piece_movement import Side
from utils.asset import PieceSetAssets, BoardAssets
from chess.chess_timer import DefaultConfigs
from config import *

pygame.init()
window_size = pygame.math.Vector2(WINDOW_SIZE)
pygame.display.set_mode(window_size)
done = False
clock = pygame.time.Clock()
prev_time = time.time()
delta_time: float = 0

match = Match(DefaultConfigs.RAPID_15_10)
white_player = Player(
    side=Side.WHITE,
    piece_set=random.choice([PieceSetAssets.NORMAL16x32, PieceSetAssets.NORMAL16x16]),
    board_asset=random.choice(list(BoardAssets)),
    scale=BOARD_SCALE,
    time_left=match.timer_config.time
)

black_player = Player(
    side=Side.BLACK,
    piece_set=random.choice([PieceSetAssets.NORMAL16x32, PieceSetAssets.NORMAL16x16]),
    board_asset=random.choice(list(BoardAssets)),
    scale=BOARD_SCALE,
    time_left=match.timer_config.time
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


def get_colors(player: Player) -> tuple[str, str]:
    bg = 'white' if player.side == Side.WHITE else 'black'
    font = 'black' if player.side == Side.WHITE else 'white'
    return bg, font


white_player.set_to_default_pos(window_size)
black_player.set_to_default_pos(window_size)

is_white = True

while not done:

    set_delta_time()

    fps = round(clock.get_fps())

    current_player = white_player if is_white else black_player
    bg_color, fg_color = get_colors(current_player)

    for event in pygame.event.get():
        if event.type == pygame.QUIT: done = True
        if event.type == pygame.KEYDOWN and current_player.state is not STATE.PICK_PROMOTION:
            is_white = not is_white
            white_player.is_render_required = True
            black_player.is_render_required = True
        current_player.parse_input(event, match.fen, local=True)

    update_window_caption(white_player, black_player)

    match.process_local_move()

    parse_command_local(match.fen, white_player, black_player)

    white_player.update(delta_time)
    black_player.update(delta_time)
    current_player.render(fg_color, bg_color)

    pygame.display.flip()

    clock.tick()

pygame.quit()
sys.exit()
