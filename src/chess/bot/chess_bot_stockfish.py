from __future__ import annotations

import datetime
import logging
import threading

from stockfish import Stockfish

from chess.board.side import Side
from chess.chess_player import Player
from chess.chess_player import send_command
from chess_engine.movement.validate_move import is_checkmate
from chess_engine.notation.algebraic_notation import AlgebraicNotation
from chess_engine.notation.forsyth_edwards_notation import Fen
from config.logging_manager import AppLoggers
from config.logging_manager import LoggingManager
from config.user_config import UserConfig
from network.commands.client_commands import ClientGameCommand
from network.commands.command_manager import CommandManager


class StockFishBot:
    stock_fish: Stockfish | None = None
    logger: logging.Logger | None = None

    @staticmethod
    def get_logger() -> logging.Logger:
        if StockFishBot.logger is None:
            StockFishBot.logger = LoggingManager.get_logger(AppLoggers.BOT)
        return StockFishBot.logger

    @staticmethod
    def create_bot(engine_path: str = "stockfish") -> bool:
        try:
            StockFishBot.stock_fish = Stockfish(engine_path)
            return True
        except FileNotFoundError:
            return False
        except OSError:
            return False

    @staticmethod
    def is_created() -> bool:
        return StockFishBot.stock_fish is not None

    @staticmethod
    def get() -> Stockfish:
        if StockFishBot.stock_fish is None:
            raise Exception('stock fish bot not created')
        return StockFishBot.stock_fish

    def __init__(self, fen: Fen, side: Side, player: Player) -> None:
        self.logger: logging.Logger = StockFishBot.get_logger()
        self.side: Side = side
        self.fen: Fen = fen
        self.player: Player = player
        self.move_thread: threading.Thread = self.get_move_thread()
        StockFishBot.get().update_engine_parameters(
            {
                "UCI_Elo": UserConfig.get().data.bot_elo,
                "Skill Level": UserConfig.get().data.bot_skill_level
            }
        )

    def get_best_move(self) -> str | None:
        player_time_left: float = self.player.timer_gui.own_timer.time_left
        bot_time_left: float = self.player.timer_gui.opponents_timer.time_left
        white_time: float = player_time_left if self.player.side is Side.WHITE else bot_time_left
        black_time: float = player_time_left if self.player.side is Side.BLACK else bot_time_left

        if is_checkmate(self.fen):
            return None

        # maybe change this to if the fen is invalid return None
        # this might be cleaner but not too sure about the implications
        assert StockFishBot.get().is_fen_valid(self.fen.notation), "fen is not valid!"
        StockFishBot.get().set_fen_position(self.fen.notation)

        if UserConfig.get().data.bot_use_time:
            return StockFishBot.get().get_best_move(wtime=int(white_time * 1000), btime=int(black_time * 1000))
        else:
            return StockFishBot.get().get_best_move()

    def get_move_thread(self) -> threading.Thread:
        return threading.Thread(target=self.make_move)

    def make_move(self, side: Side | None = None) -> None:
        if side is None: side = self.side
        move: None | str = self.get_best_move()
        self.logger.info("before move fen : %s", self.fen.notation)
        self.logger.info("found move : %s", move)
        time_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        target_fen: str | None = None

        # crashed once cause move was None so. ;)
        # crashed during bot v bot, checkmate move
        if move is None: return

        # promotion
        if len(move) == 5:
            target_fen = move[len(move) - 1:]
            move = move[:len(move) - 1]

        from_an_val, dest_an_val = move[:2], move[2:]
        from_an = AlgebraicNotation(*from_an_val)
        dest_an = AlgebraicNotation(*dest_an_val)

        if target_fen is None:
            target_fen = self.fen[from_an.index]

        ks_king_index = 62 if self.fen.is_white_turn() else 6
        qs_king_index = 58 if self.fen.is_white_turn() else 2
        king_index = 60 if self.fen.is_white_turn() else 4

        if from_an.index == king_index:
            if dest_an.index == ks_king_index:
                dest_an = AlgebraicNotation.get_an_from_index(dest_an.index + 1)
            elif dest_an.index == qs_king_index:
                dest_an = AlgebraicNotation.get_an_from_index(dest_an.index - 1)

        move_info: dict[str, str] = {CommandManager.from_coordinates: from_an.coordinates,
                                     CommandManager.dest_coordinates: dest_an.coordinates,
                                     CommandManager.side: side.name,
                                     CommandManager.target_fen: target_fen,
                                     CommandManager.time_iso: time_iso}
        move_command = CommandManager.get(ClientGameCommand.MOVE, move_info)
        send_command(True, None, move_command)

    def play_game(self) -> None:
        if self.player.game_over: return
        if not self.player.turn and not self.move_thread.is_alive():
            new_thread: threading.Thread = self.get_move_thread()
            new_thread.start()
            self.move_thread = new_thread

    def play_both_sides(self) -> None:
        if self.player.game_over: return
        if not self.move_thread.is_alive():
            side: Side = Side.WHITE if self.fen.is_white_turn() else Side.BLACK
            new_thread: threading.Thread = threading.Thread(target=self.make_move, args=(side,))
            new_thread.start()
            self.move_thread = new_thread
