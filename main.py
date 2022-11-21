import pygame, sys
import asset as ASSETS
import chess as CHESS
import player as PLAYER
import game as GAME
import commands as CMD
from utils import debug

from random import choice




pygame.init()
window_size = pygame.math.Vector2(1040, 650)
pygame.display.set_mode(window_size)
done = False
scale_factor = 4
clock = pygame.time.Clock()



white_player = PLAYER.PLAYER(
	side = CHESS.SIDE.WHITE,
	piece_set = choice(list(ASSETS.PIECE_SET)),
	board_asset = choice(list(ASSETS.BOARDS)),
	scale = scale_factor
	)

black_player = PLAYER.PLAYER(
	side = CHESS.SIDE.BLACK,
	piece_set = choice(list(ASSETS.PIECE_SET)),
	board_asset = choice(list(ASSETS.BOARDS)),
	scale = scale_factor
	)


game = GAME.GAME(white_player, black_player)

screen_center = window_size / 2

white_player.board.pos_rect.center = round(screen_center.x), round(screen_center.y)
black_player.board.pos_rect.center = round(screen_center.x), round(screen_center.y)

is_white = True


while not done:

	bg_color = white_player.side.name.lower() if white_player.turn else black_player.side.name.lower()
	font_color = white_player.side.name.lower() if not white_player.turn else black_player.side.name.lower()
	pygame.display.get_surface().fill(bg_color)

	player = white_player if is_white else black_player

	for event in pygame.event.get():
		if event.type == pygame.QUIT: done = True
		if event.type == pygame.KEYDOWN: is_white =  not is_white
		PLAYER.parse_player_input( event, player, game.FEN_notation )


	GAME.exec_player_command( game, white_player, black_player ) 
	GAME.render_board( game, player )
	GAME.render_pieces( game, player )

	debug(round(clock.get_fps()), font_color)
	pygame.display.flip()
	clock.tick()

pygame.quit()
sys.exit()