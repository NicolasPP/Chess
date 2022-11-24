import pygame, sys, random

from random import choice

from utils import asset as ASSETS
from utils import debug as DB
from chess import chess_data as CHESS
from chess import player as PLAYER
from chess import match as MATCH



pygame.init()
window_size = pygame.math.Vector2(1040, 650)
pygame.display.set_mode(window_size)
done = False
scale_factor = 4
clock = pygame.time.Clock()

match = MATCH.MATCH()
white_player = PLAYER.PLAYER(
		side =CHESS.SIDE.WHITE,
		piece_set = random.choice(list(ASSETS.PIECE_SET)),
		board_asset = random.choice(list(ASSETS.BOARDS)),
		scale = scale_factor
	)

black_player = PLAYER.PLAYER(
		side = CHESS.SIDE.BLACK,
		piece_set = random.choice(list(ASSETS.PIECE_SET)),
		board_asset = random.choice(list(ASSETS.BOARDS)),
		scale = scale_factor
	)



# placing boards in the middle of the screen
screen_center = window_size / 2
white_player.board.pos_rect.center = round(screen_center.x), round(screen_center.y)
black_player.board.pos_rect.center = round(screen_center.x), round(screen_center.y)

is_white = True


while not done:
	
	fps = round(clock.get_fps())
	bg_color = white_player.side.name.lower() if white_player.turn else black_player.side.name.lower()
	font_color = white_player.side.name.lower() if not white_player.turn else black_player.side.name.lower()
	pygame.display.get_surface().fill(bg_color)

	player = white_player if is_white else black_player

	for event in pygame.event.get():
		if event.type == pygame.QUIT: done = True
		if event.type == pygame.KEYDOWN: is_white =  not is_white
		PLAYER.parse_player_input( event, player, match.fen )



	MATCH.exec_player_command( match ) 
	PLAYER.exec_match_command( white_player, black_player, match.fen ) 
	
	PLAYER.render_board( player )
	PLAYER.render_pieces( player )

	DB.debug(fps, font_color)
	pygame.display.flip()
	clock.tick()

pygame.quit()
sys.exit()