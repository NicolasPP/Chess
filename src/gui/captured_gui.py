import dataclasses

import pygame

from chess.asset.asset_manager import AssetManager
from chess.board.side import Side
from chess.notation.forsyth_edwards_notation import validate_fen_val
from chess.asset.chess_assets import scale_surface, PieceSetAssets
from chess.game.game_surface import GameSurface
from chess.game.game_size import GameSize
from chess.notation.forsyth_edwards_notation import FenChars

from config import *


@dataclasses.dataclass
class CapturedPiecesScore:
    white: int
    black: int


@dataclasses.dataclass
class CapturedPiecesSurface:
    white: pygame.surface.Surface
    black: pygame.surface.Surface


class CapturedGui:

    @staticmethod
    def get_piece_score(piece_fen_val: str) -> int:
        if piece_fen_val.upper() == FenChars.DEFAULT_KNIGHT:
            return N_SCORE

        elif piece_fen_val.upper() == FenChars.DEFAULT_PAWN:
            return P_SCORE

        elif piece_fen_val.upper() == FenChars.DEFAULT_ROOK:
            return R_SCORE

        elif piece_fen_val.upper() == FenChars.DEFAULT_QUEEN:
            return Q_SCORE

        elif piece_fen_val.upper() == FenChars.DEFAULT_BISHOP:
            return B_SCORE

        else:
            raise Exception(f'piece_fen_val : {piece_fen_val} is not valid')

    def __init__(
            self,
            captured_pieces: str,
            board_rect: pygame.rect.Rect,
            captured_scale: float = 1 / 3
    ):
        self.captured_scale: float = captured_scale
        self.board_rect: pygame.rect.Rect = board_rect
        self.captured_pieces: str = captured_pieces
        self.pieces: dict[str, pygame.surface.Surface] = self.copy_and_resize_pieces()
        for val in captured_pieces: validate_fen_val(val)
        self.captured_surfaces: CapturedPiecesSurface = self.create_captured_surfaces()
        self.captured_score: CapturedPiecesScore = self.calculate_captured_pieces_score()
        self.pos_offset: pygame.math.Vector2 = pygame.math.Vector2(0, (X_AXIS_HEIGHT * GameSize.get_scale()))

    def set_captured_pieces(self, new_cap_pieces: str) -> None:
        self.captured_pieces = new_cap_pieces
        for val in self.captured_pieces: validate_fen_val(val)
        self.captured_surfaces = self.create_captured_surfaces()
        self.captured_score = self.calculate_captured_pieces_score()

    def calculate_captured_pieces_score(self) -> CapturedPiecesScore:
        white_score = black_score = 0
        for fen_val in self.captured_pieces:
            score = CapturedGui.get_piece_score(fen_val)
            if fen_val.isupper():
                black_score += score

            else:
                white_score += score
        return CapturedPiecesScore(white_score, black_score)

    def create_captured_surfaces(self) -> CapturedPiecesSurface:
        piece_size = self.get_piece_size()

        w_size = sum(list(map(lambda char: 1 if char.isupper() else 0, self.captured_pieces)))
        b_size = sum(list(map(lambda char: 1 if char.islower() else 0, self.captured_pieces)))

        w_surface_size = piece_size.elementwise() * pygame.math.Vector2(w_size, 1)
        b_surface_size = piece_size.elementwise() * pygame.math.Vector2(b_size, 1)

        w_captured_surface = pygame.surface.Surface(w_surface_size)
        b_captured_surface = pygame.surface.Surface(b_surface_size)

        w_captured_surface.fill(AssetManager.get_theme().dark_color)
        b_captured_surface.fill(AssetManager.get_theme().dark_color)

        w_pos = pygame.math.Vector2(0)
        b_pos = pygame.math.Vector2(0)

        for fen_val in self.captured_pieces:
            if fen_val.isupper():
                w_captured_surface.blit(self.pieces[fen_val], w_pos)
                w_pos.x += piece_size.x
            else:
                b_captured_surface.blit(self.pieces[fen_val], b_pos)
                b_pos.x += piece_size.x

        return CapturedPiecesSurface(w_captured_surface, b_captured_surface)

    def copy_and_resize_pieces(self) -> dict[str, pygame.surface.Surface]:
        copy_pieces: dict[str, pygame.surface.Surface] = {}
        for fen_val, surface in AssetManager.load_pieces_surfaces(
                PieceSetAssets.SIMPLE16x16, GameSize.get_scale()).items():
            copy_pieces[fen_val] = scale_surface(surface, self.captured_scale)
        return copy_pieces

    def render(self, player_side: Side) -> None:
        scale = GameSize.get_scale()
        top_pos = pygame.math.Vector2(self.board_rect.topleft) - pygame.math.Vector2(0, OPP_TIMER_SPACING * scale)
        bottom_pos = pygame.math.Vector2(self.board_rect.bottomleft) + self.pos_offset

        if player_side is Side.WHITE:
            w_surface_pos = top_pos
            b_surface_pos = bottom_pos
        else:
            b_surface_pos = top_pos
            w_surface_pos = bottom_pos

        top_pos.y -= self.get_piece_size().y

        GameSurface.get().blit(self.captured_surfaces.white, w_surface_pos)
        GameSurface.get().blit(self.captured_surfaces.black, b_surface_pos)

    def get_piece_size(self) -> pygame.math.Vector2:
        return pygame.math.Vector2(self.pieces['p'].get_rect().size)
