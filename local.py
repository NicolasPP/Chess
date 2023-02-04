import random
import sys

import pygame

import chess.chess_data as CHESS
import chess.match as MATCH
import chess.player as PLAYER
import utils.asset as ASSETS
import utils.debug as DB
from config import *

pygame.init()
window_size = pygame.math.Vector2(WINDOW_SIZE)
pygame.display.set_mode(window_size)
done = False
clock = pygame.time.Clock()

match = MATCH.Match()
white_player = PLAYER.Player(
    side=CHESS.SIDE.WHITE,
    piece_set=random.choice(list(ASSETS.PieceSetAssets)),
    board_asset=random.choice(list(ASSETS.BoardAssets)),
    scale=BOARD_SCALE
)

black_player = PLAYER.Player(
    side=CHESS.SIDE.BLACK,
    piece_set=random.choice(list(ASSETS.PieceSetAssets)),
    board_asset=random.choice(list(ASSETS.BoardAssets)),
    scale=BOARD_SCALE
)
white_player.update_turn(match.fen)
black_player.update_turn(match.fen)


def update_window_caption(*players: PLAYER.Player) -> None:
    for player in players:
        if player.game_over:
            pygame.display.set_caption('GAME OVER')
            return
        if not player.turn: continue
        pygame.display.set_caption(f"{player.side.name}s TURN")
        return


def get_colors(player: PLAYER.Player) -> tuple[str, str]:
    bg = 'white' if player.side == CHESS.SIDE.WHITE else 'black'
    font = 'black' if player.side == CHESS.SIDE.WHITE else 'white'
    return bg, font


# placing boards in the middle of the screen
screen_center = window_size / 2
white_player.board.pos_rect.center = round(screen_center.x), round(screen_center.y)
black_player.board.pos_rect.center = round(screen_center.x), round(screen_center.y)

is_white = True

while not done:

    fps = round(clock.get_fps())

    current_player = white_player if is_white else black_player
    bg_color, font_color = get_colors(current_player)

    for event in pygame.event.get():
        if event.type == pygame.QUIT: done = True
        if event.type == pygame.KEYDOWN:
            is_white = not is_white
            white_player.is_render_required = True
            black_player.is_render_required = True
        current_player.parse_input(event, local=True)

    update_window_caption(white_player, black_player)

    match.process_local_move()

    PLAYER.parse_command_local(match.fen, white_player, black_player)

    current_player.render(bg_color)

    DB.debug(fps, bg_color, font_color)

    pygame.display.flip()

    clock.tick()

pygame.quit()
sys.exit()
