import dataclasses

import chess.asset.chess_assets as asset_manager
import chess.notation.forsyth_edwards_notation as notation

from config import *


@dataclasses.dataclass
class PieceInfo:
    asset_index: int


class PieceAssets:
    sprites: dict[str, asset_manager.Sprite] = {}
    asset_index: dict[str, int] = {}

    @staticmethod
    def load_pieces_sprites(piece_set: asset_manager.PieceSet, scale: float) -> dict[str, asset_manager.Sprite]:
        sprites = {}
        white_sprites, black_sprites = asset_manager.load_piece_set(piece_set, scale)
        assert len(white_sprites) == len(black_sprites)
        for fen_value, index in PieceAssets.asset_index.items():
            sprites[fen_value.upper()] = white_sprites[index]
            sprites[fen_value.lower()] = black_sprites[index]
        return sprites

    @staticmethod
    def load_assets_index():
        PieceAssets.asset_index[notation.FenChars.DEFAULT_PAWN.value] = P_ASSET_INDEX
        PieceAssets.asset_index[notation.FenChars.DEFAULT_KNIGHT.value] = N_ASSET_INDEX
        PieceAssets.asset_index[notation.FenChars.DEFAULT_ROOK.value] = R_ASSET_INDEX
        PieceAssets.asset_index[notation.FenChars.DEFAULT_BISHOP.value] = B_ASSET_INDEX
        PieceAssets.asset_index[notation.FenChars.DEFAULT_QUEEN.value] = Q_ASSET_INDEX
        PieceAssets.asset_index[notation.FenChars.DEFAULT_KING.value] = K_ASSET_INDEX

    @staticmethod
    def load(piece_set: asset_manager.PieceSet, scale: float) -> None:
        PieceAssets.load_assets_index()
        PieceAssets.sprites = PieceAssets.load_pieces_sprites(piece_set, scale)
