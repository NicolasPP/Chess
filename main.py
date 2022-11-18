import pygame, sys
import asset as ASSETS
import chess as CHESS


from random import choice




pygame.init()
window_size = pygame.math.Vector2(1040, 650)
pygame.display.set_mode(window_size)
bg_color = 'green'
done = False
scale_factor = 3





game = CHESS.GAME(
		board_asset = choice(list(ASSETS.BOARDS)),
		piece_set = choice(list(ASSETS.PIECE_SET)),
		scale = scale_factor 
	)

game.board.pos_rect.center = window_size / 2


while not done:
	
	pygame.display.get_surface().fill(bg_color)

	for event in pygame.event.get():
		if event.type == pygame.QUIT: done = True

	CHESS.render( game )


	pygame.display.flip()

pygame.quit()
sys.exit()