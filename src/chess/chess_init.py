import pygame

from chess.asset.asset_manager import AssetManager
from chess.asset.chess_assets import ChessTheme
from chess.asset.chess_assets import PieceSetAsset
from chess.asset.chess_assets import PieceSetAssets
from chess.board.chess_board import Board
from chess.game.game_size import GameSize
from chess.game.game_surface import GameSurface
from chess_engine.movement.piece_movement import PieceMovement
from chess_engine.notation.forsyth_edwards_notation import FenChars
from config.pg_config import GAME_SURFACE_SPACING
from gui.board_axis_gui import AxisRects
from gui.board_axis_gui import BoardAxisGui
from gui.end_game_gui import EndGameGui
from gui.played_moves_gui import PlayedMovesGui
from gui.timer_gui import TimerGui
from gui.timer_gui import TimerRects


def init_chess(theme: ChessTheme, piece_set: PieceSetAsset, scale: float) -> None:
    GameSize.reset()
    pygame.init()

    PieceMovement.load()
    GameSize.load_scale(scale)

    board_rect: pygame.rect.Rect = Board.calculate_board_rect()
    end_game_rect: pygame.rect.Rect = EndGameGui.calculate_end_game_rect()
    timer_rects: TimerRects = TimerGui.calculate_timer_rects()
    axis_rects: AxisRects = BoardAxisGui.calculate_axis_rects()
    played_moves_bg_rect: pygame.rect.Rect = PlayedMovesGui.calculate_background_rect()
    '''
    -- width --
    y_axis board max_width(end_game, played_moves_background)
    '''
    max_rect = max(end_game_rect, played_moves_bg_rect, key=lambda rect: rect.width)
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
    GameSurface.get().fill(AssetManager.get_theme().primary_dark)
    pygame.display.get_surface().fill(AssetManager.get_theme().primary_dark)

    AssetManager.load_pieces(PieceSetAssets.NORMAL16x16, scale)
    pygame.display.set_icon(AssetManager.get_piece_surface(FenChars.get_piece_fen(FenChars.DEFAULT_KING, False)))
    AssetManager.load_pieces(piece_set, scale)


def calculate_window_size(width: int, height: int) -> tuple[int, int]:
    return width + GAME_SURFACE_SPACING, height + GAME_SURFACE_SPACING
