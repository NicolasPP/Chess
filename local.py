import pygame, sys, random

from chess import game as GAME

from utils import asset as ASSETS
from utils import debug as DB
from chess import chess_data as CHESS
from chess import player as PLAYER
from chess import match as MATCH

from config import *



pygame.init()
window_size = pygame.math.Vector2(WINDOW_SIZE)
pygame.display.set_mode(window_size)
done = False
clock = pygame.time.Clock()

match = MATCH.Match()
white_player = PLAYER.PLAYER(
		side =CHESS.SIDE.WHITE,
		piece_set = random.choice(list(ASSETS.PIECE_SET)),
		board_asset = random.choice(list(ASSETS.BOARDS)),
		scale = BOARD_SCALE
	)

black_player = PLAYER.PLAYER(
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


# placing boards in the middle of the screen
screen_center = window_size / 2
white_player.board.pos_rect.center = round(screen_center.x), round(screen_center.y)
black_player.board.pos_rect.center = round(screen_center.x), round(screen_center.y)

is_white = True


while not done:
	
	fps = round(clock.get_fps())
	bg_color = 'white' if white_player.turn else 'black'
	font_color = 'black' if white_player.turn else 'white'
	pygame.display.get_surface().fill(bg_color)

	player = white_player if is_white else black_player

	for event in pygame.event.get():
		if event.type == pygame.QUIT: done = True
		if event.type == pygame.KEYDOWN: is_white =  not is_white
		PLAYER.parse_local_player_input( event, player, match.fen )

	update_window_caption(white_player, black_player)
	MATCH.exec_player_command( match ) 
	PLAYER.exec_match_command( white_player, black_player, match.fen ) 
	
	PLAYER.render_board( player )
	PLAYER.render_pieces( player )

	DB.debug(fps, font_color)
	pygame.display.flip()
	clock.tick()

pygame.quit()
sys.exit()