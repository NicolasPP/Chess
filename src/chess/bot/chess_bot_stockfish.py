import datetime

from _thread import start_new_thread
from stockfish import Stockfish

from chess.notation.forsyth_edwards_notation import Fen
from chess.notation.algebraic_notation import AlgebraicNotation
from chess.chess_player import Player, send_command
from chess.network.command_manager import CommandManager, ClientCommand
from chess.board.side import Side


class StockFishBot:
    def __init__(self, game_fen: Fen, player: Player, side: Side) -> None:
        self.side: Side = side
        self.stockfish: Stockfish = Stockfish()
        start_new_thread(self.play_game, (player, game_fen))

    def get_best_move(self, game_fen: Fen) -> str:
        self.stockfish.is_fen_valid(game_fen.notation)
        self.stockfish.set_fen_position(game_fen.notation)
        return self.stockfish.get_best_move()

    def make_move(self, game_fen: Fen, side: Side | None = None) -> None:
        if side is None: side = self.side
        move = self.get_best_move(game_fen)
        time_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        from_an_val, dest_an_val = move[:2], move[2:]
        from_an = AlgebraicNotation(*from_an_val)
        dest_an = AlgebraicNotation(*dest_an_val)

        ks_king_index = 62 if game_fen.is_white_turn() else 6
        qs_king_index = 58 if game_fen.is_white_turn() else 2
        king_index = 60 if game_fen.is_white_turn() else 4

        if from_an.index == king_index:
            if dest_an.index == ks_king_index:
                dest_an = AlgebraicNotation.get_an_from_index(dest_an.index + 1)
            elif dest_an.index == qs_king_index:
                dest_an = AlgebraicNotation.get_an_from_index(dest_an.index - 1)

        move_info: dict[str, str] = {
            CommandManager.from_coordinates: from_an.coordinates,
            CommandManager.dest_coordinates: dest_an.coordinates,
            CommandManager.side: side.name,
            CommandManager.target_fen: game_fen[from_an.index],
            CommandManager.time_iso: time_iso
        }

        move_command = CommandManager.get(ClientCommand.MOVE, move_info)
        send_command(True, None, move_command)

    def play_game(self, player: Player, game_fen: Fen) -> None:
        while not player.game_over:
            is_turn: bool = not game_fen.is_white_turn() if self.side == Side.BLACK else game_fen.is_white_turn()
            if is_turn:
                self.make_move(game_fen)
