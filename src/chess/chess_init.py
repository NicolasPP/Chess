import pygame

from chess.movement.piece_movement import PieceMovement
from chess.asset.chess_assets import ChessTheme
from chess.asset.asset_manager import AssetManager
from gui.board_axis_gui import BoardAxisGui, AxisRects
from gui.end_game_gui import EndGameGui, EndGameRects
from chess.game.game_surface import GameSurface
from chess.game.game_size import GameSize
from gui.timer_gui import TimerGui, TimerRects
from chess.board.chess_board import Board
from config import GAME_SURFACE_SPACING


def init_chess(theme: ChessTheme, scale: float) -> None:
    pygame.init()

    AssetManager.load_theme(theme)
    PieceMovement.load()
    GameSize.load_scale(scale)

    board_rect: pygame.rect.Rect = Board.calculate_board_rect()
    timer_rects: TimerRects = TimerGui.calculate_timer_rects()
    axis_rects: AxisRects = BoardAxisGui.calculate_axis_rects()
    end_game_rects: EndGameRects = EndGameGui.calculate_end_game_rects()
    '''
    -- width --
    y_axis
    board
    max_width(resign, draw)
    '''
    max_rect = end_game_rects.resign_rect \
        if end_game_rects.resign_rect.width >= end_game_rects.draw_rect.width else end_game_rects.draw_rect
    GameSize.add_rects_width(axis_rects.y_axis, board_rect, max_rect)

    '''
       -- height --
       timer
       timer_spacing
       board
       x_axis
       timer
    '''
    GameSize.add_rects_height(
        timer_rects.timer,
        timer_rects.spacing,
        board_rect,
        axis_rects.x_axis,
        timer_rects.timer)

    GameSurface.create_surface()

    pygame.display.set_mode(calculate_window_size(GameSurface.get()))
    pygame.display.get_surface().fill(AssetManager.get_theme().dark_color)


def calculate_window_size(surface: pygame.surface.Surface) -> tuple[int, int]:
    width, height = surface.get_size()
    bigger_side = max(width, height)
    return bigger_side + GAME_SURFACE_SPACING, bigger_side + GAME_SURFACE_SPACING
