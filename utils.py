import pygame
pygame.font.init()
font = pygame.font.Font(None, 30)
font_color = 'gray'


def debug(info, y = 10, x = 10):
    debug_render = font.render(str(info),True,font_color)
    debug_rect = debug_render.get_rect(topleft = (x,y))
    pygame.display.get_surface().blit(debug_render, debug_rect)