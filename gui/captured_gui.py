import pygame
import utils.Forsyth_Edwards_notation as FEN
import chess.chess_data as CHESS
import utils.asset as ASSETS


class CapturedPieces:
    def __init__(self, captured_pieces: str, pieces: dict[str, CHESS.Piece], scale: float = 3 / 5):
        self.scale = scale
        self._captured_pieces = captured_pieces
        for val in captured_pieces: FEN.validate_fen_val(val)
        self.pieces = self.resize_pieces(pieces)
        self.surface = self.create_captured_surface()

    @property
    def captured_pieces(self) -> str:
        return self._captured_pieces

    @captured_pieces.setter
    def captured_pieces(self, new_cap_pieces) -> None:
        self._captured_pieces = new_cap_pieces
        for val in self.captured_pieces: FEN.validate_fen_val(val)
        self.surface = self.create_captured_surface()

    @captured_pieces.deleter
    def captured_pieces(self) -> None:
        del self._captured_pieces

    def create_captured_surface(self) -> pygame.surface.Surface:
        piece_size = pygame.math.Vector2(self.pieces['p'].sprite.surface.get_rect().size)
        surface_size = piece_size.elementwise() * pygame.math.Vector2(len(self.captured_pieces), 1)
        captured_surface = pygame.surface.Surface(surface_size)
        pos = pygame.math.Vector2(0)
        for fen_val in self.captured_pieces:
            captured_surface.blit(self.pieces[fen_val].sprite.surface, pos)
            pos.x += piece_size.x
        return captured_surface

    def resize_pieces(self, pieces: dict[str, CHESS.Piece]) -> dict[str, CHESS.Piece]:
        for fen_val, piece in pieces.items():
            pieces[fen_val].sprite.surface = ASSETS.scale(piece.sprite.surface, self.scale)
        return pieces

    def render(self, pos: pygame.math.Vector2) -> None:
        pygame.display.get_surface().blit(self.surface, pos)
