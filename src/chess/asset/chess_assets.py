import dataclasses
import math
import random
import typing

import pygame

from config.pg_config import *


@dataclasses.dataclass
class ChessTheme:
    primary_light: tuple[int, int, int]
    primary_dark: tuple[int, int, int]
    secondary_light: tuple[int, int, int]
    secondary_dark: tuple[int, int, int]


@dataclasses.dataclass
class PieceSetAsset:
    white_assets_file: str
    black_assets_file: str


class PieceSurfaces(typing.NamedTuple):
    white: list[pygame.surface.Surface]
    black: list[pygame.surface.Surface]


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
    PLAIN1: ChessTheme = ChessTheme(THEME1_P_LIGHT, THEME1_P_DARK, THEME1_S_LIGHT, THEME1_S_DARK)
    PLAIN2: ChessTheme = ChessTheme(THEME2_P_LIGHT, THEME2_P_DARK, THEME2_S_LIGHT, THEME2_S_DARK)
    PLAIN3: ChessTheme = ChessTheme(THEME3_P_LIGHT, THEME3_P_DARK, THEME3_S_LIGHT, THEME3_S_DARK)
    PLAIN4: ChessTheme = ChessTheme(THEME4_P_LIGHT, THEME4_P_DARK, THEME4_S_LIGHT, THEME4_S_DARK)

    @staticmethod
    def get_theme(theme_id: int) -> ChessTheme:
        if theme_id == -1: return random.choice([Themes.PLAIN1, Themes.PLAIN2, Themes.PLAIN3, Themes.PLAIN4])
        if theme_id == 0: return Themes.PLAIN1
        if theme_id == 1: return Themes.PLAIN2
        if theme_id == 2: return Themes.PLAIN3
        if theme_id == 3:
            return Themes.PLAIN4
        else:
            raise Exception(f'theme_id : {theme_id} is not a valid theme_id')

    @staticmethod
    def get_name(theme_id: int) -> str:
        if theme_id == -1: return "RANDOM"
        if theme_id == 0: return "0"
        if theme_id == 1: return "1"
        if theme_id == 2: return "2"
        if theme_id == 3: return "3"
        else:
            raise Exception(f'theme_id : {theme_id} is not a valid theme_id')


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


def load_surface_sheet(asset_file: str, asset_scale: float) -> list[pygame.surface.Surface]:
    sheet_surface: pygame.surface.Surface = load_surface(asset_file, surface_scale=1)
    sheet_dimensions = pygame.math.Vector2(PIECE_ASSET_COL, PIECE_ASSET_ROW)
    sheet_size = pygame.math.Vector2(sheet_surface.get_size()).elementwise()
    surface_size = sheet_size / sheet_dimensions

    surfaces: list[pygame.surface.Surface] = []

    for surface, index in sheet_surface_gen(surface_size):
        surface.blit(sheet_surface, surface_size * index * -1)
        surface = scale_surface(surface, asset_scale)
        surfaces.append(surface)

    return surfaces


def load_surface(file: str, surface_scale: float) -> pygame.surface.Surface:
    surface = pygame.image.load(file).convert()
    surface = scale_surface(surface, surface_scale)
    return surface


def load_piece_set(piece_set: PieceSetAsset, piece_scale: float) -> PieceSurfaces:
    return PieceSurfaces(load_surface_sheet(piece_set.white_assets_file, piece_scale),
        load_surface_sheet(piece_set.black_assets_file, piece_scale))
