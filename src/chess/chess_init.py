import pygame

from chess.movement.piece_movement import PieceMovement
from chess.asset.chess_assets import ChessTheme, PieceSetAsset, PieceSetAssets
from chess.asset.asset_manager import AssetManager
from gui.board_axis_gui import BoardAxisGui, AxisRects
from gui.end_game_gui import EndGameGui
from chess.game.game_surface import GameSurface
from chess.game.game_size import GameSize
from gui.timer_gui import TimerGui, TimerRects
from gui.played_moves_gui import PlayedMovesGui, PlayedMovesRects
from chess.board.chess_board import Board
from chess.notation.forsyth_edwards_notation import FenChars
from config import GAME_SURFACE_SPACING


def init_chess(theme: ChessTheme, piece_set: PieceSetAsset, scale: float) -> None:
    pygame.init()

    PieceMovement.load()
    GameSize.load_scale(scale)

    board_rect: pygame.rect.Rect = Board.calculate_board_rect()
    end_game_rect: pygame.rect.Rect = EndGameGui.calculate_end_game_rect()
    timer_rects: TimerRects = TimerGui.calculate_timer_rects()
    axis_rects: AxisRects = BoardAxisGui.calculate_axis_rects()
    played_moves_rects: PlayedMovesRects = PlayedMovesGui.calculate_played_moves_rects()
    '''
    -- width --
    y_axis board max_width(end_game, played_moves_background)
    '''
    max_rect = max(end_game_rect, played_moves_rects.background, key=lambda rect: rect.width)
    GameSize.add_rects_width(axis_rects.y_axis, board_rect, max_rect)

    '''
       -- height --
       timer timer_spacing board x_axis timer
    '''
    GameSize.add_rects_height(timer_rects.timer, timer_rects.spacing, board_rect, axis_rects.x_axis, timer_rects.timer)

    GameSurface.create_surface()
    pygame.display.set_mode(calculate_window_size(*GameSurface.get().get_size()))
    pygame.display.set_caption("")

    AssetManager.load_theme(theme)
    GameSurface.get().fill(AssetManager.get_theme().dark_color)
    pygame.display.get_surface().fill(AssetManager.get_theme().dark_color)

    AssetManager.load_pieces(PieceSetAssets.NORMAL16x16, scale)
    pygame.display.set_icon(AssetManager.get_piece_surface(FenChars.get_piece_fen(FenChars.DEFAULT_KING, False)))
    AssetManager.load_pieces(piece_set, scale)


def calculate_window_size(width: int, height: int) -> tuple[int, int]:
    return width + GAME_SURFACE_SPACING, height + GAME_SURFACE_SPACING
