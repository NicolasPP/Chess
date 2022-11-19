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
	piece_set = ASSETS.PIECE_SET.NORMAL16x32,
	board_asset = choice(list(ASSETS.BOARDS)),
	scale = scale_factor
	)

black_player = PLAYER.PLAYER(
	side = CHESS.SIDE.BLACK,
	piece_set = ASSETS.PIECE_SET.NORMAL16x32,
	board_asset = choice(list(ASSETS.BOARDS)),
	scale = scale_factor
	)


game = GAME.GAME(white_player, black_player, fen_notation ='rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R')

white_player.board.pos_rect.center = window_size / 2
black_player.board.pos_rect.center = window_size / 2

is_white = True

while not done:
	
	pygame.display.get_surface().fill(bg_color)

	player = white_player if is_white else black_player

	for event in pygame.event.get():
		if event.type == pygame.QUIT: done = True
		if event.type == pygame.KEYDOWN: is_white =  not is_white
		GAME.parse_player_input( event, player )


	GAME.render_board( game, player )
	GAME.render_pieces( game, player )

	pygame.display.flip()

pygame.quit()
sys.exit()