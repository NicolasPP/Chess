import pygame, sys
import asset as ASSETS
import chess as CHESS





pygame.init()
window_size = pygame.math.Vector2(1040, 650)
pygame.display.set_mode(window_size)
bg_color = 'green'
done = False
scale_factor = 3





game = CHESS.GAME(
		board_asset = ASSETS.BOARDS.BOARD_PLAIN2,
		piece_set = ASSETS.PIECE_SET.NORMAL16x32,
		scale = scale_factor 
	)


while not done:
	
	pygame.display.get_surface().fill(bg_color)

	for event in pygame.event.get():
		if event.type == pygame.QUIT: done = True

	pygame.display.get_surface().blit(game.board.sprite.surface, game.board.pos_rect)

	pygame.display.flip()

pygame.quit()
sys.exit()