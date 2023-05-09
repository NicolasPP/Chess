import time

import pygame

from chess.game.chess_match import Match
from chess.chess_player import Player, process_command_local, State
from chess.board.side import Side
from chess.asset.chess_assets import ChessTheme, PieceSetAsset
from chess.timer.timer_config import TimerConfig
from chess.game.game_surface import GameSurface
from chess.chess_init import init_chess
from chess.notation.forsyth_edwards_notation import Fen
from chess.bot.chess_bot_stockfish import StockFishBot


class OfflineLauncher:
    def __init__(self) -> None:
        self.prev_time = time.time()
        self.delta_time: float = 0

    def set_delta_time(self) -> None:
        now = time.time()
        self.delta_time = now - self.prev_time
        self.prev_time = now

    def launch_against_bot(
            self,
            theme: ChessTheme,
            scale: float,
            piece_set:PieceSetAsset,
            timer_config: TimerConfig
    ) -> None:
        done = False
        init_chess(theme, piece_set, scale)
        center: pygame.rect.Rect = GameSurface.get().get_rect(center=pygame.display.get_surface().get_rect().center)
        match: Match = Match(timer_config)
        player: Player = Player.get_player_local(Side.WHITE, match, center)
        game_fen: Fen = Fen()
        stock_fish = StockFishBot(game_fen, player, Side.BLACK)

        while not done:

            self.set_delta_time()

            for event in pygame.event.get():
                keys = pygame.key.get_pressed()
                if event.type == pygame.KEYDOWN:
                    if keys[pygame.K_SPACE]:
                        stock_fish.make_move(game_fen, Side.WHITE)
                if event.type == pygame.QUIT:
                    done = True
                player.parse_input(event, game_fen, local=True)
            match.process_local_move()
            process_command_local(game_fen, player)
            player.update(self.delta_time, local=True)
            player.render()

            pygame.display.get_surface().blit(GameSurface.get(), center)

            pygame.display.flip()

        pygame.quit()

    def launch_against_human(
            self,
            theme: ChessTheme,
            scale: float,
            piece_set: PieceSetAsset,
            timer_config: TimerConfig
    ) -> None:
        done = False
        is_white = True
        init_chess(theme, piece_set, scale)
        center: pygame.rect.Rect = GameSurface.get().get_rect(center=pygame.display.get_surface().get_rect().center)
        match = Match(timer_config)
        white_player: Player = Player.get_player_local(Side.WHITE, match, center)
        black_player: Player = Player.get_player_local(Side.BLACK, match, center)
        game_fen: Fen = Fen()
        while not done:

            self.set_delta_time()

            current_player = white_player if is_white else black_player

            for event in pygame.event.get():
                keys = pygame.key.get_pressed()
                if event.type == pygame.QUIT: done = True
                if event.type == pygame.KEYDOWN:
                    if keys[pygame.K_SPACE] and current_player.state is not State.PICKING_PROMOTION:
                        is_white = not is_white
                        white_player.set_require_render(True)
                        black_player.set_require_render(True)
                current_player.parse_input(event, game_fen, local=True)

            match.process_local_move()

            process_command_local(game_fen, white_player, black_player)

            white_player.update(self.delta_time, local=True)
            black_player.update(self.delta_time, local=True)
            current_player.render()

            pygame.display.get_surface().blit(GameSurface.get(), center)

            pygame.display.flip()

        pygame.quit()
