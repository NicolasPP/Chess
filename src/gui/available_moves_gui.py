import typing

import pygame

from chess.notation.forsyth_edwards_notation import Fen, FenChars
from chess.movement.piece_movement import get_available_moves
from chess.game.game_surface import GameSurface
from chess.board.chess_board import Board
from chess.board.side import Side
from chess.board.board_tile import BoardTile
from config import *


class AvailableMovesGui:
    def __init__(self) -> None:
        self.available_moves: dict[int, list[int]] = {index: [] for index in range(BOARD_SIZE * BOARD_SIZE)}

    def update_available_moves(self, fen: Fen, side: Side, piece_index: int) -> None:
        is_black_and_lower = side is Side.BLACK and fen[piece_index].islower()
        is_white_and_upper = side is Side.WHITE and fen[piece_index].isupper()
        correct_side = True if is_black_and_lower or is_white_and_upper else False
        if fen[piece_index] == FenChars.BLANK_PIECE.value or not correct_side:
            self.available_moves[piece_index] = []
            return None
        available_moves = get_available_moves(piece_index, fen)
        self.available_moves[piece_index] = available_moves

    def render(self, picked: BoardTile, board: Board, side: Side, turn: bool) -> None:
        if not turn: return
        if side is Side.WHITE:
            if picked.fen_val.islower(): return
        if side is Side.BLACK:
            if picked.fen_val.isupper(): return
        for surface, pos in self.get_available_moves_surface(picked, board):
            GameSurface.get().blit(surface, pos)

    def get_available_moves_surface(self, picked: BoardTile, board: Board) -> \
            typing.Generator[tuple[pygame.surface.Surface, pygame.math.Vector2], None, None]:
        board_offset = pygame.math.Vector2(board.rect.topleft)
        for index in self.available_moves[picked.algebraic_notation.data.index]:
            tile = board.grid[index]
            tile_size = pygame.math.Vector2(tile.rect.size) * AVAILABLE_MOVE_SCALE
            available_surface = pygame.surface.Surface(tile_size)
            pos = available_surface.get_rect(center=tile.rect.center)
            available_surface.fill(AVAILABLE_MOVE_COLOR)
            available_surface.set_alpha(AVAILABLE_ALPHA)
            yield available_surface, board_offset + pygame.math.Vector2(pos.topleft)
