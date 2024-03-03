from __future__ import annotations

import datetime
from threading import Thread
from typing import Optional

from chess_engine.movement.validate_move import is_checkmate
from chess_engine.notation.algebraic_notation import AlgebraicNotation
from chess_engine.notation.forsyth_edwards_notation import Fen
from stockfish import Stockfish
from stockfish.models import StockfishException

from chess.board.side import Side
from chess.chess_player import Player
from config.user_config import UserConfig
from event.game_events import MoveEvent
from event.local_event_queue import LocalEvents


class StockFishBot:
    stock_fish: Stockfish | None = None

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
    def get() -> Stockfish:
        if StockFishBot.stock_fish is None:
            raise Exception('stock fish bot not created')
        return StockFishBot.stock_fish

    def __init__(self, fen: Fen, side: Side, player: Player) -> None:
        self.side: Side = side
        self.fen: Fen = fen
        self.player: Player = player
        self.move_thread: Thread = self.get_move_thread()
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
        # this might be cleaner but not so sure about the implications
        assert StockFishBot.get().is_fen_valid(self.fen.notation), "fen is not valid!"
        StockFishBot.get().set_fen_position(self.fen.notation)

        try:
            if UserConfig.get().data.bot_use_time:
                return StockFishBot.get().get_best_move(wtime=int(white_time * 1000), btime=int(black_time * 1000))
            else:
                return StockFishBot.get().get_best_move()

        except StockfishException:
            return None

    def get_move_thread(self, side: Optional[Side] = None) -> Thread:
        if side is None:
            return Thread(target=self.make_move, daemon=True)

        return Thread(target=self.make_move, args=(side,), daemon=True)

    def make_move(self, side: Side | None = None) -> None:
        if side is None:
            side = self.side

        move: None | str = self.get_best_move()
        time_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        target_fen: str | None = None

        # crashed once cause move was None so. ;)
        # crashed during bot v bot, checkmate move
        if move is None:
            return

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

        move_event: MoveEvent = MoveEvent(-1, (from_an.file, from_an.rank), (dest_an.file, dest_an.rank),
                                          side.name, target_fen, time_iso)
        LocalEvents.get().add_match_event(move_event)

    def play_game(self) -> None:
        if self.player.game_over:
            return

        if self.player.turn:
            return

        if self.move_thread.is_alive():
            return

        self.move_thread = self.get_move_thread()
        self.move_thread.start()

    def play_both_sides(self) -> None:
        if self.player.game_over:
            return

        if self.move_thread.is_alive():
            return

        self.move_thread = self.get_move_thread(Side.WHITE if self.fen.is_white_turn() else Side.BLACK)
        self.move_thread.start()
