import time

import pygame

from chess.game.chess_match import Match
from chess.chess_player import Player, process_command_local, State
from chess.board.side import Side
from chess.asset.chess_assets import Themes, PieceSetAssets
from chess.timer.timer_config import DefaultConfigs
from chess.game.game_surface import GameSurface
from chess.chess_init import init_chess
from chess.notation.forsyth_edwards_notation import Fen
from chess.bot.chess_bot_stockfish import StockFishBot
from config.user_config import UserConfig

from config.pg_config import MOUSECLICK_SCROLL_UP, MOUSECLICK_SCROLL_DOWN


class OfflineLauncher:
    def __init__(self) -> None:
        self.prev_time = time.time()
        self.delta_time: float = 0

    def set_delta_time(self) -> None:
        now = time.time()
        self.delta_time = now - self.prev_time
        self.prev_time = now

    def launch_against_bot(self) -> None:
        done = False
        bot_side: Side = Side[UserConfig.get().data.bot_side_name]
        player_side: Side = Side.WHITE if bot_side == Side.BLACK else Side.BLACK
        init_chess(
            Themes.get_theme(UserConfig.get().data.theme_id),
            PieceSetAssets.get_asset(UserConfig.get().data.asset_name),
            UserConfig.get().data.scale
        )
        center: pygame.rect.Rect = GameSurface.get().get_rect(center=pygame.display.get_surface().get_rect().center)
        match = Match(DefaultConfigs.get_timer_config(UserConfig.get().data.timer_config_name))
        player: Player = Player.get_player_local(player_side, match, center)
        player.end_game_gui.offer_draw.set_enable(False)
        player.end_game_gui.resign.set_enable(False)
        game_fen: Fen = Fen(match.fen.notation)
        stock_fish: StockFishBot = StockFishBot(game_fen, bot_side, player)
        while not done:

            self.set_delta_time()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                player.parse_input(event, game_fen, local=True)

            stock_fish.play_game()
            match.process_local_move()
            process_command_local(game_fen, player)
            player.update(self.delta_time, local=True)
            player.render()

            pygame.display.get_surface().blit(GameSurface.get(), center)

            pygame.display.flip()

        pygame.quit()

    def launch_bot_vs_bot(self) -> None:
        done = False
        perspective_side: Side = Side[UserConfig.get().data.bot_side_name]
        opp_side: Side = Side.WHITE if perspective_side == Side.BLACK else Side.BLACK
        init_chess(
            Themes.get_theme(UserConfig.get().data.theme_id),
            PieceSetAssets.get_asset(UserConfig.get().data.asset_name),
            UserConfig.get().data.scale
        )
        center: pygame.rect.Rect = GameSurface.get().get_rect(center=pygame.display.get_surface().get_rect().center)
        match = Match(DefaultConfigs.get_timer_config(UserConfig.get().data.timer_config_name))
        player: Player = Player.get_player_local(perspective_side, match, center)
        bot_player: Player = Player.get_player_local(opp_side, match, center)
        bot_player.set_final_render(False)
        player.end_game_gui.offer_draw.set_enable(False)
        player.end_game_gui.resign.set_enable(False)
        game_fen: Fen = Fen(match.fen.notation)
        stock_fish: StockFishBot = StockFishBot(game_fen, opp_side, player)
        while not done:

            self.set_delta_time()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == MOUSECLICK_SCROLL_UP:
                        player.played_moves_gui.scroll_up(player.game_offset)
                    if event.button == MOUSECLICK_SCROLL_DOWN:
                        player.played_moves_gui.scroll_down(player.game_offset)

            stock_fish.play_both_sides()
            match.process_local_move()
            process_command_local(game_fen, player, bot_player)
            player.update(self.delta_time, local=True)
            bot_player.update(self.delta_time, local=True)
            player.render()

            pygame.display.get_surface().blit(GameSurface.get(), center)

            pygame.display.flip()

        pygame.quit()

    def launch_against_human(self) -> None:
        done = False
        is_white = True
        init_chess(
            Themes.get_theme(UserConfig.get().data.theme_id),
            PieceSetAssets.get_asset(UserConfig.get().data.asset_name),
            UserConfig.get().data.scale
        )
        center: pygame.rect.Rect = GameSurface.get().get_rect(center=pygame.display.get_surface().get_rect().center)
        match = Match(DefaultConfigs.get_timer_config(UserConfig.get().data.timer_config_name))
        white_player: Player = Player.get_player_local(Side.WHITE, match, center)
        black_player: Player = Player.get_player_local(Side.BLACK, match, center)
        game_fen: Fen = Fen(match.fen.notation)
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
