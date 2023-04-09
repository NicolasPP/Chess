import dataclasses

from chess.asset.chess_assets import Sprite, PieceSetAsset, load_piece_set, ChessTheme
import chess.notation.forsyth_edwards_notation as notation

from config import *


@dataclasses.dataclass
class PieceInfo:
    asset_index: int


class AssetManager:
    piece_sprites: dict[str, Sprite] = {}
    piece_asset_index: dict[str, int] = {}
    theme: ChessTheme

    @staticmethod
    def load_pieces_sprites(piece_set: PieceSetAsset, scale: float) -> dict[str, Sprite]:
        sprites = {}
        white_sprites, black_sprites = load_piece_set(piece_set, scale)
        assert len(white_sprites) == len(black_sprites)
        for fen_value, index in AssetManager.piece_asset_index.items():
            sprites[fen_value.upper()] = white_sprites[index]
            sprites[fen_value.lower()] = black_sprites[index]
        return sprites

    @staticmethod
    def load_assets_index():
        AssetManager.piece_asset_index[notation.FenChars.DEFAULT_PAWN.value] = P_ASSET_INDEX
        AssetManager.piece_asset_index[notation.FenChars.DEFAULT_KNIGHT.value] = N_ASSET_INDEX
        AssetManager.piece_asset_index[notation.FenChars.DEFAULT_ROOK.value] = R_ASSET_INDEX
        AssetManager.piece_asset_index[notation.FenChars.DEFAULT_BISHOP.value] = B_ASSET_INDEX
        AssetManager.piece_asset_index[notation.FenChars.DEFAULT_QUEEN.value] = Q_ASSET_INDEX
        AssetManager.piece_asset_index[notation.FenChars.DEFAULT_KING.value] = K_ASSET_INDEX

    @staticmethod
    def load_pieces(piece_set: PieceSetAsset, scale: float) -> None:
        AssetManager.load_assets_index()
        AssetManager.piece_sprites = AssetManager.load_pieces_sprites(piece_set, scale)

    @staticmethod
    def load_theme(theme: ChessTheme) -> None:
        AssetManager.theme = theme

    @staticmethod
    def get_piece(fen_val: str) -> Sprite:
        sprite = AssetManager.piece_sprites.get(fen_val)
        if sprite is None:
            raise Exception(f'fen_val : {fen_val} not found, make sure piece assets are loaded')
        return sprite

    @staticmethod
    def get_theme() -> ChessTheme:
        return AssetManager.theme
