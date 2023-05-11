import datetime
import threading
from stockfish import Stockfish

from chess.notation.forsyth_edwards_notation import Fen
from chess.notation.algebraic_notation import AlgebraicNotation
from chess.chess_player import Player, send_command
from chess.network.command_manager import CommandManager, ClientCommand
from chess.board.side import Side


class StockFishBot:
    def __init__(self, fen: Fen, side: Side, player: Player) -> None:
        self.side: Side = side
        self.fen: Fen = fen
        self.player: Player = player
        # FIXME: this will only work on my machine :(
        # assume stockfish installed globally,
        # TODO: create field in launcher to specify path to stockfish engine binary folder
        self.stock_fish: Stockfish = Stockfish(
            path=r"C:\Users\nicol\Documents\chess-engine\stockfish_15.1_win_x64_popcnt\stockfish_15.1_win_x64_popcnt\stockfish-windows-2022-x86-64-modern.exe")
        self.move_thread: threading.Thread = self.get_move_thread()

    def get_best_move(self) -> str:
        player_time_left: float = self.player.timer_gui.own_timer.time_left
        bot_time_left: float = self.player.timer_gui.opponents_timer.time_left
        white_time: float = player_time_left if self.player.side is Side.WHITE else bot_time_left
        black_time: float = player_time_left if self.player.side is Side.BLACK else bot_time_left
        assert self.stock_fish.is_fen_valid(self.fen.notation), "fen is not valid!"
        self.stock_fish.set_fen_position(self.fen.notation)
        return self.stock_fish.get_best_move(wtime=int(white_time*1000), btime=int(black_time*1000))

    def get_move_thread(self) -> threading.Thread:
        return threading.Thread(target=self.make_move)

    def make_move(self, side: Side | None = None) -> None:
        if side is None: side = self.side
        move = self.get_best_move()
        time_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        target_fen: str | None = None

        # promotion
        if len(move) == 5:
            target_fen = move[len(move)-1:]
            move = move[:len(move)-1]

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

        move_info: dict[str, str] = {
            CommandManager.from_coordinates: from_an.coordinates,
            CommandManager.dest_coordinates: dest_an.coordinates,
            CommandManager.side: side.name,
            CommandManager.target_fen: target_fen,
            CommandManager.time_iso: time_iso
        }

        move_command = CommandManager.get(ClientCommand.MOVE, move_info)
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
