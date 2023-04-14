import pygame

from chess.board.board_tile import BoardTile
from chess.notation.forsyth_edwards_notation import FenChars
from chess.asset.asset_manager import AssetManager
from chess.movement.piece_movement import Side
from chess.game.game_surface import GameSurface
from chess.game.game_size import GameSize
from config import *


class Board:

    @staticmethod
    def calculate_board_rect() -> pygame.rect.Rect:
        return pygame.rect.Rect(
            (0, 0),
            ((SQUARE_SIZE * BOARD_SIZE * GameSize.get_scale()) + (BOARD_OUTLINE_THICKNESS * 2),
             (SQUARE_SIZE * BOARD_SIZE * GameSize.get_scale()) + (BOARD_OUTLINE_THICKNESS * 2)))

    @staticmethod
    def create_board_grid(side: Side) -> list[BoardTile]:
        grid = []
        size = pygame.math.Vector2(SQUARE_SIZE * GameSize.get_scale())
        outline_thickness = pygame.math.Vector2(BOARD_OUTLINE_THICKNESS)
        for index in BoardTile.get_board_tiles_index(side):
            pos = pygame.math.Vector2(index.col * size.x, index.row * size.y)
            rect = pygame.rect.Rect(pos + outline_thickness, size)
            grid.append(BoardTile(rect, index.algebraic_notation))
        if side is Side.BLACK: grid = grid[::-1]
        return grid

    @staticmethod
    def create_board_surface(tiles: list[BoardTile]) -> pygame.surface.Surface:
        board_surface = pygame.surface.Surface(Board.calculate_board_rect().size)
        board_surface.fill(AssetManager.get_theme().light_color)
        counter = 0
        for tile in tiles:
            surface = pygame.surface.Surface(tile.rect.size)
            if counter % 2 == 0:
                surface.fill(AssetManager.get_theme().light_color)
            else:
                surface.fill(AssetManager.get_theme().dark_color)

            if (tile.algebraic_notation.data.index + 1) % BOARD_SIZE != 0:
                counter += 1

            board_surface.blit(surface, tile.rect.topleft)

        return board_surface

    def __init__(self, side: Side):
        self.grid: list[BoardTile] = Board.create_board_grid(side)
        self.surface: pygame.surface.Surface = Board.create_board_surface(self.grid)

        self.rect: pygame.rect.Rect = self.surface.get_rect()

    def get_rect(self) -> pygame.rect.Rect:
        return self.rect

    def reload_theme(self) -> None:
        self.surface = Board.create_board_surface(self.grid)

    def reset_picked_up(self) -> None:
        for sqr in self.grid: sqr.picked_up = False

    def get_picked_up(self) -> BoardTile:
        for sqr in self.grid:
            if sqr.picked_up: return sqr
        raise Exception(' no piece picked up ')

    def set_picked_up(self, tile: BoardTile) -> None:
        if tile.fen_val == FenChars.BLANK_PIECE.value: return
        self.reset_picked_up()
        tile.picked_up = True

    def get_collided_tile(self, game_offset: pygame.rect.Rect,
                          mouse_pos: tuple[int, int] | None = None) -> BoardTile | None:
        if mouse_pos is None: mouse_pos = pygame.mouse.get_pos()
        board_offset = pygame.math.Vector2(self.rect.topleft) + pygame.math.Vector2(game_offset.topleft)
        for tile in self.grid:
            rect = tile.rect.copy()
            top_left = board_offset + pygame.math.Vector2(rect.topleft)
            rect.topleft = int(top_left.x), int(top_left.y)
            if rect.collidepoint(mouse_pos):
                return tile
        return None

    def render(self) -> None:
        GameSurface.get().blit(self.surface, self.rect)

    def render_pieces(self, is_white: bool) -> None:
        grid = self.grid if is_white else self.grid[::-1]
        for tile in grid:
            if tile.fen_val == FenChars.BLANK_PIECE.value: continue
            if tile.picked_up: continue
            tile.render(self.rect.topleft)
