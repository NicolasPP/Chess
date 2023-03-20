import random
import sys
import time

import pygame

import chess.board as chess_board
from chess.match import Match
from chess.player import Player, parse_command_local, STATE
from utils.asset import PieceSetAssets, BoardAssets
import chess.chess_timer as chess_timer
from config import *

pygame.init()
window_size = pygame.math.Vector2(WINDOW_SIZE)
pygame.display.set_mode(window_size)
done = False
clock = pygame.time.Clock()
prev_time = time.time()
delta_time = 0

match = Match(chess_timer.DefaultConfigs.RAPID_15_10)
white_player = Player(
    side=chess_board.SIDE.WHITE,
    piece_set=random.choice([PieceSetAssets.NORMAL16x32, PieceSetAssets.NORMAL16x16]),
    board_asset=random.choice(list(BoardAssets)),
    scale=BOARD_SCALE
)

black_player = Player(
    side=chess_board.SIDE.BLACK,
    piece_set=random.choice([PieceSetAssets.NORMAL16x32, PieceSetAssets.NORMAL16x16]),
    board_asset=random.choice(list(BoardAssets)),
    scale=BOARD_SCALE
)
white_player.update_turn(match.fen)
black_player.update_turn(match.fen)


def set_delta_time():
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
    bg = 'white' if player.side == chess_board.SIDE.WHITE else 'black'
    font = 'black' if player.side == chess_board.SIDE.WHITE else 'white'
    return bg, font


# placing boards in the middle of the screen
screen_center = window_size / 2
white_player.board.pos_rect.center = round(screen_center.x), round(screen_center.y)
black_player.board.pos_rect.center = round(screen_center.x), round(screen_center.y)

is_white = True

while not done:

    set_delta_time()

    fps = round(clock.get_fps())

    current_player = white_player if is_white else black_player
    bg_color, font_color = get_colors(current_player)

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

    current_player.render(bg_color)
    pygame.display.flip()

    clock.tick()

pygame.quit()
sys.exit()
