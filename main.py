import pygame, sys
import asset as ASSETS
import chess as CHESS
import player as PLAYER
import game as GAME

from random import choice




pygame.init()
window_size = pygame.math.Vector2(1040, 650)
pygame.display.set_mode(window_size)
bg_color = 'green'
done = False
scale_factor = 4



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

game = GAME.GAME()

white_player.board.pos_rect.center = window_size / 2
black_player.board.pos_rect.center = window_size / 2


while not done:
	
	pygame.display.get_surface().fill(bg_color)

	for event in pygame.event.get():
		if event.type == pygame.QUIT: done = True


	GAME.render_board( game, black_player )
	GAME.render_pieces( game, black_player )

	pygame.display.flip()

pygame.quit()
sys.exit()