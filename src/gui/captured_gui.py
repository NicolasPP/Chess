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
    score: pygame.surface.Surface


class CapturedGui:

    @staticmethod
    def get_font() -> pygame.font.Font:
        return pygame.font.Font(FONT_FILE, int(GameSize.get_relative_size(SCORE_FONT_SIZE)))

    @staticmethod
    def create_captured_dict(captured_pieces: str) -> dict[str, int]:
        captured_dict: dict[str, int] = {}
        for piece in captured_pieces:
            if piece in captured_dict:
                captured_dict[piece] += 1
            else:
                captured_dict[piece] = 1
        return captured_dict

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
            captured_scale: float = 7 / 20
    ):
        for val in captured_pieces: validate_fen_val(val)
        self.captured_scale: float = captured_scale
        self.board_rect: pygame.rect.Rect = board_rect
        self.captured_pieces: dict[str, int] = CapturedGui.create_captured_dict(captured_pieces)
        self.pieces: dict[str, pygame.surface.Surface] = self.copy_and_resize_pieces()
        self.score: CapturedPiecesScore = self.calculate_captured_pieces_score()
        self.captured_surfaces: CapturedPiecesSurface = self.create_captured_surfaces()
        self.pos_offset: pygame.math.Vector2 = pygame.math.Vector2(0, (X_AXIS_HEIGHT * GameSize.get_scale()))

    def set_captured_pieces(self, new_cap_pieces: str) -> None:
        for val in new_cap_pieces: validate_fen_val(val)
        self.captured_pieces = CapturedGui.create_captured_dict(new_cap_pieces)
        self.score = self.calculate_captured_pieces_score()
        self.captured_surfaces = self.create_captured_surfaces()

    def calculate_captured_pieces_score(self) -> CapturedPiecesScore:
        white_score = black_score = 0
        for fen_val, count in self.captured_pieces.items():
            score = CapturedGui.get_piece_score(fen_val) * count
            if fen_val.isupper():
                black_score += score

            else:
                white_score += score
        return CapturedPiecesScore(white_score, black_score)

    def create_captured_surfaces(self) -> CapturedPiecesSurface:
        piece_size = self.get_piece_size()

        w_surface_size: pygame.math.Vector2 = pygame.math.Vector2(0, piece_size.y)
        b_surface_size: pygame.math.Vector2 = pygame.math.Vector2(0, piece_size.y)

        for piece, count in self.captured_pieces.items():
            if piece.isupper():
                w_surface_size.x += (piece_size.x // 2) * count
                w_surface_size.x += (piece_size.x // 2)
            else:
                b_surface_size.x += (piece_size.x // 2) * count
                b_surface_size.x += (piece_size.x // 2)

        score_surface = pygame.surface.Surface(CapturedGui.get_font().size(MAX_SCORE))
        w_captured_surface = pygame.surface.Surface(w_surface_size)
        b_captured_surface = pygame.surface.Surface(b_surface_size)

        score_surface.fill(AssetManager.get_theme().primary_dark)
        w_captured_surface.fill(AssetManager.get_theme().primary_dark)
        b_captured_surface.fill(AssetManager.get_theme().primary_dark)

        score: str = '+' + str(abs(self.score.white - self.score.black))
        font_render: pygame.surface.Surface = CapturedGui.get_font().render(score, True,
                                                                            AssetManager.get_theme().primary_light)
        score_rect = font_render.get_rect(center=score_surface.get_rect().center)
        score_surface.blit(font_render, score_rect)

        w_pos = pygame.math.Vector2(0)
        b_pos = pygame.math.Vector2(0)
        piece_keys: list[str] = list(self.captured_pieces.keys())
        piece_keys.sort(key=lambda p: (CapturedGui.get_piece_score(p), p))
        for piece in piece_keys:
            if piece.isupper():
                for _ in range(self.captured_pieces[piece]):
                    w_captured_surface.blit(self.pieces[piece], w_pos)
                    w_pos.x += (piece_size.x // 2)
                w_pos.x += (piece_size.x // 2)
            else:
                for _ in range(self.captured_pieces[piece]):
                    b_captured_surface.blit(self.pieces[piece], b_pos)
                    b_pos.x += (piece_size.x // 2)
                b_pos.x += (piece_size.x // 2)

        return CapturedPiecesSurface(w_captured_surface, b_captured_surface, score_surface)

    def copy_and_resize_pieces(self) -> dict[str, pygame.surface.Surface]:
        copy_pieces: dict[str, pygame.surface.Surface] = {}
        for fen_val, surface in AssetManager.load_pieces_surfaces(
                PieceSetAssets.SIMPLE16x16, GameSize.get_scale()).items():
            copy_pieces[fen_val] = scale_surface(surface, self.captured_scale)
        return copy_pieces

    def render(self, player_side: Side) -> None:
        scale = GameSize.get_scale()
        top_pos = pygame.rect.Rect(*self.board_rect.topleft, 0, 0)
        top_pos.y -= int((OPP_TIMER_SPACING * scale) + self.get_piece_size().y)
        bottom_pos = pygame.rect.Rect(*self.board_rect.bottomleft, 0, 0)
        bottom_pos.x += int(self.pos_offset.x)
        bottom_pos.y += int(self.pos_offset.y)

        score_imbalance: bool = True

        if self.score.white == self.score.black:
            score_imbalance = False

        if self.score.white - self.score.black > 0 and score_imbalance:
            greater_material_side = Side.WHITE

        else:
            greater_material_side = Side.BLACK

        own_captured_surface = self.captured_surfaces.black \
            if player_side == Side.WHITE else self.captured_surfaces.white
        opp_captured_surface = self.captured_surfaces.white \
            if player_side == Side.WHITE else self.captured_surfaces.black
        if greater_material_side == player_side:
            score_pos = pygame.rect.Rect(bottom_pos)
            score_pos.x += own_captured_surface.get_width()

        else:
            score_pos = pygame.rect.Rect(top_pos)
            score_pos.x += opp_captured_surface.get_width()

        if player_side is Side.WHITE:
            w_surface_pos = top_pos
            b_surface_pos = bottom_pos
        else:
            b_surface_pos = top_pos
            w_surface_pos = bottom_pos

        GameSurface.get().blit(self.captured_surfaces.white, w_surface_pos)
        GameSurface.get().blit(self.captured_surfaces.black, b_surface_pos)
        if score_imbalance:
            GameSurface.get().blit(self.captured_surfaces.score, score_pos)

    def get_piece_size(self) -> pygame.math.Vector2:
        return pygame.math.Vector2(self.pieces[FenChars.DEFAULT_PAWN].get_rect().size)
