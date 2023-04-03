import dataclasses

from chess.asset.chess_assets import Sprite, PieceSetAsset, load_piece_set, BoardAsset, BoardSprite, load_board
import chess.notation.forsyth_edwards_notation as notation

from config import *


@dataclasses.dataclass
class PieceInfo:
    asset_index: int


class AssetManager:
    piece_sprites: dict[str, Sprite] = {}
    piece_asset_index: dict[str, int] = {}
    board_sprite: BoardSprite | None = None

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
    def load_board(board_asset: BoardAsset, scale: float) -> None:
        AssetManager.board_sprite = load_board(board_asset, scale)

    @staticmethod
    def get_piece(fen_val: str) -> Sprite:
        sprite = AssetManager.piece_sprites.get(fen_val)
        if sprite is None:
            raise Exception(f'fen_val : {fen_val} not found, make sure piece assets are loaded')
        return sprite

    @staticmethod
    def get_board() -> BoardSprite:
        if AssetManager.board_sprite is None:
            raise Exception('make sure board asset is loaded')
        return AssetManager.board_sprite
