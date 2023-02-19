import pygame
import utils.Forsyth_Edwards_notation as FEN
import chess.chess_data as CHESS
import utils.asset as ASSETS


class CapturedGui:
    def __init__(
            self,
            captured_pieces: str,
            pieces: dict[str, CHESS.Piece],
            board_rect: pygame.rect.Rect,
            bg_color: str,
            scale: float = 3 / 5
    ):
        self.scale = scale
        self.board_rect = board_rect
        self.captured_pieces = captured_pieces
        self.bg_color = bg_color
        for val in captured_pieces: FEN.validate_fen_val(val)
        self.pieces: dict[str, pygame.surface.Surface] = self.copy_and_resize_pieces(pieces)
        self.white_cap_surface, self.black_cap_surface = self.create_captured_surfaces()

    def set_captured_pieces(self, new_cap_pieces) -> None:
        self.captured_pieces = new_cap_pieces
        for val in self.captured_pieces: FEN.validate_fen_val(val)
        self.white_cap_surface, self.black_cap_surface = self.create_captured_surfaces()

    def create_captured_surfaces(self) -> tuple[pygame.surface.Surface, pygame.surface.Surface]:
        piece_size = self.get_piece_size()

        w_size = sum(list(map(lambda char: 1 if char.isupper() else 0, self.captured_pieces)))
        b_size = sum(list(map(lambda char: 1 if char.islower() else 0, self.captured_pieces)))

        w_surface_size = piece_size.elementwise() * pygame.math.Vector2(w_size, 1)
        b_surface_size = piece_size.elementwise() * pygame.math.Vector2(b_size, 1)

        w_captured_surface = pygame.surface.Surface(w_surface_size)
        b_captured_surface = pygame.surface.Surface(b_surface_size)

        w_captured_surface.fill(self.bg_color)
        b_captured_surface.fill(self.bg_color)

        w_pos = pygame.math.Vector2(0)
        b_pos = pygame.math.Vector2(0)

        for fen_val in self.captured_pieces:
            if fen_val.isupper():
                w_captured_surface.blit(self.pieces[fen_val], w_pos)
                w_pos.x += piece_size.x
            else:
                b_captured_surface.blit(self.pieces[fen_val], b_pos)
                b_pos.x += piece_size.x

        return w_captured_surface, b_captured_surface

    def copy_and_resize_pieces(self, pieces: dict[str, CHESS.Piece]) -> dict[str, pygame.surface.Surface]:
        copy_pieces: dict[str, pygame.surface.Surface] = {}
        for fen_val, piece in pieces.items():
            copy_pieces[fen_val] = ASSETS.scale(piece.sprite.surface, self.scale)
        return copy_pieces

    def render(self, player_side: CHESS.SIDE) -> None:
        top_pos = self.get_top_board_cap_pos()
        bottom_pos = self.get_bottom_board_cap_pos()

        if player_side is CHESS.SIDE.WHITE:
            w_surface_pos = top_pos
            b_surface_pos = bottom_pos
        else:
            b_surface_pos = top_pos
            w_surface_pos = bottom_pos

        top_pos.y -= self.get_piece_size().y

        pygame.display.get_surface().blit(self.white_cap_surface, w_surface_pos)
        pygame.display.get_surface().blit(self.black_cap_surface, b_surface_pos)

    def get_top_board_cap_pos(self) -> pygame.math.Vector2:
        return pygame.math.Vector2(self.board_rect.topleft)

    def get_bottom_board_cap_pos(self) -> pygame.math.Vector2:
        return pygame.math.Vector2(self.board_rect.bottomleft)

    def get_piece_size(self) -> pygame.math.Vector2:
        return pygame.math.Vector2(self.pieces['p'].get_rect().size)
