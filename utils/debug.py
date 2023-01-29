import pygame
pygame.font.init()
font = pygame.font.Font(None, 30)

def debug(info, bg_color = 'white', font_color = 'black', y = 10, x = 10):
    debug_render = font.render(str(info),True,font_color)
    debug_rect = debug_render.get_rect(topleft = (x,y))
    bg_surface = pygame.Surface(debug_rect.size)
    bg_surface.fill(bg_color)
    pygame.display.get_surface().blit(bg_surface, debug_rect)
    pygame.display.get_surface().blit(debug_render, debug_rect)