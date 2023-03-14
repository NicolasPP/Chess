import pygame

import src.chess.board as chess_board
import src.chess.piece as chess_piece


class PromotionGui:
    def __init__(self, side: chess_board.SIDE, board_rect: pygame.rect.Rect):
        self.possible_pieces: list[str] \
            = ['N', 'R', 'B', 'Q'] if side is chess_board.SIDE.WHITE else ['n', 'r', 'b', 'q']
        self.promotion_pieces: list[tuple[pygame.surface.Surface, pygame.rect.Rect, str]] \
            = self.get_promotion_pieces(board_rect)

    def get_promotion_pieces(self, board_rect: pygame.rect.Rect) \
            -> list[tuple[pygame.surface.Surface, pygame.rect.Rect, str]]:
        center = pygame.math.Vector2(board_rect.center)
        piece_width = chess_piece.Pieces.sprites[self.possible_pieces[0]].surface.get_width()
        piece_height = chess_piece.Pieces.sprites[self.possible_pieces[0]].surface.get_height()
        center.x -= (piece_width * 2)
        result = []
        for val in self.possible_pieces:
            rect = pygame.rect.Rect(center.x, center.y, piece_width, piece_height)
            result.append((chess_piece.Pieces.sprites[val].surface, rect, val))
            center.x += piece_width
        return result

    def render(self):
        for surface, rect, val in self.promotion_pieces:
            pygame.display.get_surface().blit(surface, rect)
