import pygame
import random
import sys

from chess import chess_data as CHESS
from chess import match as MATCH
from chess import player as PLAYER
from config import *
from utils import asset as ASSETS
from utils import debug as DB

pygame.init()
window_size = pygame.math.Vector2(WINDOW_SIZE)
pygame.display.set_mode(window_size)
done = False
clock = pygame.time.Clock()

match = MATCH.Match()
white_player = PLAYER.Player(
		side =CHESS.SIDE.WHITE,
		piece_set = random.choice(list(ASSETS.PIECE_SET)),
		board_asset = random.choice(list(ASSETS.BOARDS)),
		scale = BOARD_SCALE
	)

black_player = PLAYER.Player(
		side = CHESS.SIDE.BLACK,
		piece_set = random.choice(list(ASSETS.PIECE_SET)),
		board_asset = random.choice(list(ASSETS.BOARDS)),
		scale = BOARD_SCALE
	)

def update_window_caption(*players : PLAYER.Player) -> None:
	for player in players:
		if player.turn: 
			pygame.display.set_caption(f"{player.side.name}s TURN")
			return

def get_colors(player : PLAYER.Player) -> tuple[str, str]:
	bg_color = 'white' if player.side == CHESS.SIDE.WHITE else 'black'
	font_color = 'black' if player.side == CHESS.SIDE.WHITE else 'white'
	return bg_color, font_color

# placing boards in the middle of the screen
screen_center = window_size / 2
white_player.board.pos_rect.center = round(screen_center.x), round(screen_center.y)
black_player.board.pos_rect.center = round(screen_center.x), round(screen_center.y)

is_white = True

while not done:
	
	fps = round(clock.get_fps())

	player = white_player if is_white else black_player
	bg_color, font_color = get_colors(player)
	for event in pygame.event.get():
		if event.type == pygame.QUIT: done = True
		if event.type == pygame.KEYDOWN: 
			is_white =  not is_white
			white_player.is_render_required = True
			black_player.is_render_required = True
		player.parse_input( event, match.fen, local = True)

	update_window_caption(white_player, black_player)
	match.process_local_move()
	PLAYER.parse_command_local(match.fen, white_player, black_player)

	player.render(bg_color)

	DB.debug(fps, bg_color, font_color)
	pygame.display.flip()
	clock.tick()

pygame.quit()
sys.exit()