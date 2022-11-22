import pygame, sys
from random import choice

import asset as ASSETS
import chess as CHESS
import player as PLAYER
import commands as CMD
import match as MATCH
from utils import debug






pygame.init()
window_size = pygame.math.Vector2(1040, 650)
pygame.display.set_mode(window_size)
done = False
scale_factor = 4
clock = pygame.time.Clock()

match = MATCH.MATCH(
		white_piece_set =choice(list(ASSETS.PIECE_SET)),
		white_board_asset =choice(list(ASSETS.BOARDS)),
		black_piece_set =choice(list(ASSETS.PIECE_SET)),
		black_board_asset =choice(list(ASSETS.BOARDS)),
		scale = scale_factor
	)

# placing boards in the middle of the screen
screen_center = window_size / 2
match.white_player.board.pos_rect.center = round(screen_center.x), round(screen_center.y)
match.black_player.board.pos_rect.center = round(screen_center.x), round(screen_center.y)

is_white = True


while not done:

	bg_color = match.white_player.side.name.lower() if match.white_player.turn else match.black_player.side.name.lower()
	font_color = match.white_player.side.name.lower() if not match.white_player.turn else match.black_player.side.name.lower()
	pygame.display.get_surface().fill(bg_color)

	player = match.white_player if is_white else match.black_player

	for event in pygame.event.get():
		if event.type == pygame.QUIT: done = True
		if event.type == pygame.KEYDOWN: is_white =  not is_white
		PLAYER.parse_player_input( event, player, match.fen.notation )



	MATCH.exec_player_command( match ) 
	PLAYER.exec_match_command( match.white_player, match.black_player, match.fen ) 
	
	PLAYER.render_board( player )
	PLAYER.render_pieces( player )

	debug(round(clock.get_fps()), font_color)
	pygame.display.flip()
	clock.tick()

pygame.quit()
sys.exit()