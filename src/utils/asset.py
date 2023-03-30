import dataclasses
import enum
import pygame

from config import *


class TYPE(enum.Enum):
    SPRITE: int = 0
    SHEET: int = 1


@dataclasses.dataclass
class Asset:
    file: str
    a_type: TYPE


@dataclasses.dataclass
class BoardAsset:
    asset: Asset
    background: tuple[int, int, int]
    foreground: tuple[int, int, int]


@dataclasses.dataclass
class Sprite:
    surface: pygame.surface.Surface
    scale: float


@dataclasses.dataclass
class BoardSprite:
    sprite: Sprite
    background: tuple[int, int, int]
    foreground: tuple[int, int, int]


@dataclasses.dataclass
class PieceSet:
    white_asset: Asset
    black_asset: Asset


class BoardAssets(enum.Enum):
    PLAIN1: BoardAsset = BoardAsset(Asset(PLAIN1_FILE, TYPE.SPRITE), PLAIN1_BG, PLAIN1_FG)
    PLAIN2: BoardAsset = BoardAsset(Asset(PLAIN2_FILE, TYPE.SPRITE), PLAIN2_BG, PLAIN2_FG)
    PLAIN3: BoardAsset = BoardAsset(Asset(PLAIN3_FILE, TYPE.SPRITE), PLAIN3_BG, PLAIN3_FG)
    PLAIN4: BoardAsset = BoardAsset(Asset(PLAIN4_FILE, TYPE.SPRITE), PLAIN4_BG, PLAIN4_FG)


class PieceSetAssets(enum.Enum):
    SIMPLE16x16: PieceSet = PieceSet(
        white_asset=Asset(SIMPLE16x16_PIECE_FILE_WHITE, TYPE.SHEET),
        black_asset=Asset(SIMPLE16x16_PIECE_FILE_BLACK, TYPE.SHEET)
    )
    NORMAL16x16: PieceSet = PieceSet(
        white_asset=Asset(NORMAL16x16_PIECE_FILE_WHITE, TYPE.SHEET),
        black_asset=Asset(NORMAL16x16_PIECE_FILE_BLACK, TYPE.SHEET)
    )
    NORMAL16x32: PieceSet = PieceSet(
        white_asset=Asset(NORMAL16x32_PIECE_FILE_WHITE, TYPE.SHEET),
        black_asset=Asset(NORMAL16x32_PIECE_FILE_BLACK, TYPE.SHEET)
    )


def scale(surface: pygame.surface.Surface, surface_scale: float) -> pygame.surface.Surface:
    size = pygame.math.Vector2(surface.get_size()) * surface_scale
    return pygame.transform.scale(surface, (round(size.x), round(size.y)))


def sheet_surface_gen(surface_size: pygame.math.Vector2):
    for r in range(PIECE_ASSET_ROW):
        for c in range(PIECE_ASSET_COL):
            surface = pygame.surface.Surface(surface_size)
            surface.set_colorkey(PIECE_BG)
            index = pygame.math.Vector2(c, r).elementwise()
            yield surface, index


def load_sprite_sheet(asset: Asset, asset_scale: float) -> list[Sprite]:
    sheet_sprite = load_sprite(asset.file, sprite_scale=1)
    sheet_dimensions = pygame.math.Vector2(PIECE_ASSET_COL, PIECE_ASSET_ROW)
    sheet_size = pygame.math.Vector2(sheet_sprite.surface.get_size()).elementwise()
    surface_size = sheet_size / sheet_dimensions

    sprites = []

    for surface, index in sheet_surface_gen(surface_size):
        surface.blit(sheet_sprite.surface, surface_size * index * -1)
        surface = scale(surface, asset_scale)
        sprites.append(Sprite(surface, asset_scale))

    return sprites


def load_sprite(file: str, sprite_scale: float) -> Sprite:
    surface = pygame.image.load(file).convert()
    surface = scale(surface, sprite_scale)
    return Sprite(surface, sprite_scale)


def load_board(board_asset: BoardAsset, asset_scale: float) -> BoardSprite:
    return BoardSprite(load_sprite(board_asset.asset.file, asset_scale), board_asset.background, board_asset.foreground)


def load_piece_set(piece_set: PieceSet, piece_scale: float) -> tuple[list[Sprite], list[Sprite]]:
    return load_sprite_sheet(piece_set.white_asset, piece_scale), load_sprite_sheet(piece_set.black_asset, piece_scale)
