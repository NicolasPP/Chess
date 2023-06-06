import pygame

from chess.asset.asset_manager import AssetManager
from chess.asset.chess_assets import scale_surface
from chess.board.side import Side
from chess.game.game_surface import GameSurface
from config.pg_config import PROMOTION_PIECE_SCALE


class PromotionGui:
    def __init__(self, side: Side, board_rect: pygame.rect.Rect):
        self.possible_pieces: list[str] \
            = ['N', 'R', 'B', 'Q'] if side is Side.WHITE else ['n', 'r', 'b', 'q']
        self.promotion_pieces: list[tuple[pygame.surface.Surface, pygame.rect.Rect, str]] \
            = self.get_promotion_pieces(board_rect)

    def get_promotion_pieces(self, board_rect: pygame.rect.Rect) \
            -> list[tuple[pygame.surface.Surface, pygame.rect.Rect, str]]:
        center = pygame.math.Vector2(board_rect.center)
        p_surface = scale_surface(AssetManager.get_piece_surface(self.possible_pieces[0]), PROMOTION_PIECE_SCALE)
        piece_width, piece_height = p_surface.get_size()
        center.x -= (piece_width * 2)
        result = []
        for val in self.possible_pieces:
            rect = pygame.rect.Rect(center.x, center.y, piece_width, piece_height)
            result.append((scale_surface(AssetManager.get_piece_surface(val), PROMOTION_PIECE_SCALE), rect, val))
            center.x += piece_width
        return result

    def render(self):
        for surface, rect, val in self.promotion_pieces:
            GameSurface.get().blit(surface, rect)
