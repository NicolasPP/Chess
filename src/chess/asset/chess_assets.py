import dataclasses
import math
import random

import pygame

from config import *


@dataclasses.dataclass
class ChessTheme:
    light_color: tuple[int, int, int]
    dark_color: tuple[int, int, int]


@dataclasses.dataclass
class PieceSetAsset:
    white_assets_file: str
    black_assets_file: str


@dataclasses.dataclass
class Sprite:
    surface: pygame.surface.Surface
    scale: float


class PieceSetAssets:
    SIMPLE16x16: PieceSetAsset = PieceSetAsset(SIMPLE16x16_PIECE_FILE_WHITE, SIMPLE16x16_PIECE_FILE_BLACK)
    NORMAL16x16: PieceSetAsset = PieceSetAsset(NORMAL16x16_PIECE_FILE_WHITE, NORMAL16x16_PIECE_FILE_BLACK)
    NORMAL16x32: PieceSetAsset = PieceSetAsset(NORMAL16x32_PIECE_FILE_WHITE, NORMAL16x32_PIECE_FILE_BLACK)

    @staticmethod
    def get_asset(name: str) -> PieceSetAsset:
        if name == 'RANDOM':
            return random.choice([PieceSetAssets.NORMAL16x16, PieceSetAssets.NORMAL16x32])

        elif name == 'SMALL':
            return PieceSetAssets.NORMAL16x16

        elif name == 'LARGE':
            return PieceSetAssets.NORMAL16x32

        else:
            raise Exception(f'piece_set name : {name} not recognised')


class Themes:
    PLAIN1: ChessTheme = ChessTheme(PLAIN1_LIGHT, PLAIN1_DARK)
    PLAIN2: ChessTheme = ChessTheme(PLAIN2_LIGHT, PLAIN2_DARK)
    PLAIN3: ChessTheme = ChessTheme(PLAIN3_LIGHT, PLAIN3_DARK)
    PLAIN4: ChessTheme = ChessTheme(PLAIN4_LIGHT, PLAIN4_DARK)

    @staticmethod
    def get_theme(theme_id: int) -> ChessTheme:
        if theme_id == -1: return random.choice([Themes.PLAIN1, Themes.PLAIN2, Themes.PLAIN3, Themes.PLAIN4])
        if theme_id == 1: return Themes.PLAIN1
        if theme_id == 2: return Themes.PLAIN2
        if theme_id == 3: return Themes.PLAIN3
        if theme_id == 4: return Themes.PLAIN4
        else: raise Exception(f'theme_id : {theme_id} is not a valid theme_id')


def scale_surface(surface: pygame.surface.Surface, surface_scale: float) -> pygame.surface.Surface:
    size = pygame.math.Vector2(surface.get_size()) * surface_scale
    return pygame.transform.scale(surface, (math.floor(size.x), math.floor(size.y)))


def sheet_surface_gen(surface_size: pygame.math.Vector2):
    for r in range(PIECE_ASSET_ROW):
        for c in range(PIECE_ASSET_COL):
            surface = pygame.surface.Surface(surface_size)
            surface.set_colorkey(PIECE_BG)
            index = pygame.math.Vector2(c, r).elementwise()
            yield surface, index


def load_sprite_sheet(asset_file: str, asset_scale: float) -> list[Sprite]:
    sheet_sprite = load_sprite(asset_file, sprite_scale=1)
    sheet_dimensions = pygame.math.Vector2(PIECE_ASSET_COL, PIECE_ASSET_ROW)
    sheet_size = pygame.math.Vector2(sheet_sprite.surface.get_size()).elementwise()
    surface_size = sheet_size / sheet_dimensions

    sprites = []

    for surface, index in sheet_surface_gen(surface_size):
        surface.blit(sheet_sprite.surface, surface_size * index * -1)
        surface = scale_surface(surface, asset_scale)
        sprites.append(Sprite(surface, asset_scale))

    return sprites


def load_sprite(file: str, sprite_scale: float) -> Sprite:
    surface = pygame.image.load(file).convert()
    surface = scale_surface(surface, sprite_scale)
    return Sprite(surface, sprite_scale)


def load_piece_set(piece_set: PieceSetAsset, piece_scale: float) -> tuple[list[Sprite], list[Sprite]]:
    return load_sprite_sheet(piece_set.white_assets_file, piece_scale), \
           load_sprite_sheet(piece_set.black_assets_file, piece_scale)
