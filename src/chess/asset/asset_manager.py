import pygame

from chess.asset.chess_assets import ChessTheme
from chess.asset.chess_assets import PieceSetAsset
from chess.asset.chess_assets import PieceSurfaces
from chess.asset.chess_assets import load_piece_set
from chess.notation.forsyth_edwards_notation import FenChars
from config.pg_config import B_ASSET_INDEX
from config.pg_config import K_ASSET_INDEX
from config.pg_config import N_ASSET_INDEX
from config.pg_config import P_ASSET_INDEX
from config.pg_config import Q_ASSET_INDEX
from config.pg_config import R_ASSET_INDEX


class AssetManager:
    piece_surfaces: dict[str, pygame.surface.Surface] = {}
    piece_asset_index: dict[str, int] = {}
    theme: ChessTheme | None = None

    @staticmethod
    def load_pieces_surfaces(piece_set: PieceSetAsset, scale: float) -> dict[str, pygame.surface.Surface]:
        surfaces: dict[str, pygame.surface.Surface] = {}
        piece_surfaces: PieceSurfaces = load_piece_set(piece_set, scale)
        assert len(piece_surfaces.white) == len(piece_surfaces.black)
        for fen_value, index in AssetManager.piece_asset_index.items():
            surfaces[fen_value.upper()] = piece_surfaces.white[index]
            surfaces[fen_value.lower()] = piece_surfaces.black[index]
        return surfaces

    @staticmethod
    def load_assets_index():
        AssetManager.piece_asset_index[FenChars.DEFAULT_PAWN] = P_ASSET_INDEX
        AssetManager.piece_asset_index[FenChars.DEFAULT_KNIGHT] = N_ASSET_INDEX
        AssetManager.piece_asset_index[FenChars.DEFAULT_ROOK] = R_ASSET_INDEX
        AssetManager.piece_asset_index[FenChars.DEFAULT_BISHOP] = B_ASSET_INDEX
        AssetManager.piece_asset_index[FenChars.DEFAULT_QUEEN] = Q_ASSET_INDEX
        AssetManager.piece_asset_index[FenChars.DEFAULT_KING] = K_ASSET_INDEX

    @staticmethod
    def load_pieces(piece_set: PieceSetAsset, scale: float) -> None:
        AssetManager.load_assets_index()
        AssetManager.piece_surfaces = AssetManager.load_pieces_surfaces(piece_set, scale)

    @staticmethod
    def load_theme(theme: ChessTheme) -> None:
        AssetManager.theme = theme

    @staticmethod
    def get_piece_surface(fen_val: str) -> pygame.surface.Surface:
        surface = AssetManager.piece_surfaces.get(fen_val)
        if surface is None:
            raise Exception(f'fen_val : {fen_val} not found, make sure piece assets are loaded')
        return surface

    @staticmethod
    def get_theme() -> ChessTheme:
        if AssetManager.theme is None:
            raise Exception('theme is not loaded')
        return AssetManager.theme
