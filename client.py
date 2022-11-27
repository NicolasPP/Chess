import pygame, sys, random

from random import choice

from utils import asset as ASSETS
from utils import debug as DB
from chess import chess_data as CHESS
from chess import player as PLAYER
from utils import FEN_notation as FENN
import network as NET


from config import NO_MOVE

pygame.init()
window_size = pygame.math.Vector2(1040, 650)
pygame.display.set_mode(window_size)
done = False
scale_factor = 4
clock = pygame.time.Clock()
network = NET.Network()


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


player = white_player if network.id % 2 == 0 else black_player

# placing boards in the middle of the screen
screen_center = window_size / 2
player.board.pos_rect.center = round(screen_center.x), round(screen_center.y)

is_white = True

bg_color = 'white'
font_color = 'black'


fen = network.send(NO_MOVE)
match_fen = FENN.Fen( fen )

while not done:
	
	fps = round(clock.get_fps())
	pygame.display.get_surface().fill(bg_color)

	fen = network.send(NO_MOVE)
	print( fen )
	match_fen.notation = fen

	for event in pygame.event.get():
		if event.type == pygame.QUIT: done = True
		PLAYER.parse_player_input( event, player, match_fen, network )

	PLAYER.update_pieces_location(player, match_fen)

	PLAYER.render_board( player )
	PLAYER.render_pieces( player )

	DB.debug(fps, font_color)
	pygame.display.flip()
	clock.tick()

pygame.quit()
sys.exit()