import pygame

from chess.piece_movement import PieceMovement
from chess.asset.chess_assets import ChessTheme
from chess.asset.asset_manager import AssetManager
from gui.board_axis_gui import BoardAxisGui, AxisRects
from gui.end_game_gui import EndGameGui, EndGameRects
from chess.game_surface import GameSurface

from chess.board import Board
from gui.timer_gui import TimerGui, TimerRects

from config import GAME_SURFACE_SPACING


def init_chess(theme: ChessTheme, scale: float) -> None:
    pygame.init()

    AssetManager.load_theme(theme)
    PieceMovement.load()

    board_rect: pygame.rect.Rect = Board.calculate_board_rect(scale)
    timer_rects: TimerRects = TimerGui.calculate_timer_rects(scale)
    axis_rects: AxisRects = BoardAxisGui.calculate_axis_rects(scale)
    end_game_rects: EndGameRects = EndGameGui.calculate_end_game_rects()
    '''
    -- width --
    y_axis
    board
    max_width(resign, draw)
    '''
    max_rect = end_game_rects.resign_rect \
        if end_game_rects.resign_rect.width >= end_game_rects.draw_rect.width else end_game_rects.draw_rect
    GameSurface.add_rects_width(axis_rects.y_axis, board_rect, max_rect)

    '''
       -- height --
       timer
       timer_spacing
       board
       x_axis
       timer
    '''
    GameSurface.add_rects_height(
        timer_rects.timer,
        timer_rects.spacing,
        board_rect,
        axis_rects.x_axis,
        timer_rects.timer)

    GameSurface.create_surface()

    pygame.display.set_mode(calculate_window_size(GameSurface.surface))
    pygame.display.get_surface().fill(AssetManager.get_theme().dark_color)


def calculate_window_size(surface: pygame.surface.Surface) -> tuple[int, int]:
    width, height = surface.get_size()
    bigger_side = max(width, height)
    return bigger_side + GAME_SURFACE_SPACING, bigger_side + GAME_SURFACE_SPACING
