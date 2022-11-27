import network as NET
import pygame
pygame.init()
n = NET.Network()

done = False
p = pygame.display.set_mode((50, 50))

r = ''

while not done:
	for event in pygame.event.get():
		if event.type == pygame.QUIT: done = True
		if event.type == pygame.MOUSEBUTTONDOWN: r = n.send('its the client')
	
	pygame.display.flip()

	if r:
		print( r )
		r = ''




