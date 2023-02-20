import pygame

import chess.chess_data as CHESS


class PromotionGui:
    def __init__(self, pieces: dict[str, CHESS.Piece], side: CHESS.SIDE, board_rect: pygame.rect.Rect):
        self.possible_pieces: list[str] \
            = ['N', 'R', 'B', 'Q'] if side is CHESS.SIDE.WHITE else ['n', 'r', 'b', 'q']
        self.promotion_pieces: list[tuple[pygame.surface.Surface, pygame.rect.Rect, str]] \
            = self.get_promotion_pieces(pieces, board_rect)

    def get_promotion_pieces(self, pieces: dict[str, CHESS.Piece], board_rect: pygame.rect.Rect) \
            -> list[tuple[pygame.surface.Surface, pygame.rect.Rect, str]]:
        center = pygame.math.Vector2(board_rect.center)
        piece_width = pieces[self.possible_pieces[0]].sprite.surface.get_width()
        piece_height = pieces[self.possible_pieces[0]].sprite.surface.get_height()
        center.x -= (piece_width * 2)
        result = []
        for val in self.possible_pieces:
            rect = pygame.rect.Rect(center.x, center.y, piece_width, piece_height)
            result.append((pieces[val].sprite.surface, rect, val))
            center.x += piece_width
        return result

    def render(self):
        for surface, rect, val in self.promotion_pieces:
            pygame.display.get_surface().blit(surface, rect)
