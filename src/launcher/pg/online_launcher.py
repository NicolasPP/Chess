import socket
import time
from typing import Optional

import pygame
from chess_engine.notation.forsyth_edwards_notation import Fen

from chess.asset.chess_assets import PieceSetAssets
from chess.asset.chess_assets import Themes
from chess.board.side import Side
from chess.chess_init import init_chess
from chess.chess_player import Player
from chess.game.game_surface import GameSurface
from config.logging_manager import AppLoggers
from config.logging_manager import LoggingManager
from config.user_config import UserConfig
from network.commands.client_commands import ClientGameCommand
from network.commands.command_manager import CommandManager


class OnlineLauncher:

    def __init__(self) -> None:
        self.logger = LoggingManager.get_logger(AppLoggers.ONLINE_LAUNCHER)
        self.prev_time = time.time()
        self.delta_time: float = 0
        self.player: Optional[Player] = None
        self.match_fen: Fen = Fen()

    def set_delta_time(self) -> None:
        now = time.time()
        self.delta_time = now - self.prev_time
        self.prev_time = now

    def get_player(self) -> Optional[Player]:
        return self.player

    def reset_fen(self) -> None:
        self.match_fen = Fen()

    def create_player(self, side: str, time_: float, match_id: int, offset: pygame.rect.Rect) -> Player:
        player: Player = Player(Side[side], time_, offset)
        player.set_match_id(match_id)
        self.player = player
        return player

    def launch(self, connection: socket.socket, time_: float, side: str, match_id: int) -> None:
        init_chess(
            Themes.get_theme(UserConfig.get().data.theme_id),
            PieceSetAssets.get_asset(UserConfig.get().data.asset_name),
            UserConfig.get().data.scale
        )
        center = GameSurface.get().get_rect(center=pygame.display.get_surface().get_rect().center)

        self.reset_fen()
        player: Player = self.create_player(side, time_, match_id, center)

        player.update_turn(self.match_fen)
        player.update_pieces_location(self.match_fen)

        done = False
        while not done:
            self.set_delta_time()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if not player.game_over:
                        resign_info: dict[str, str] = {CommandManager.side: player.side.name}
                        resign = CommandManager.get(ClientGameCommand.RESIGN, resign_info)
                        player.send_command(resign, connection)
                        pygame.quit()

                    done = True

                player.parse_input(event, self.match_fen, connection)

            player.render()
            player.update(self.delta_time, connection)
            if (screen := pygame.display.get_surface()) is None:
                return

            screen.blit(GameSurface.get(), center)
            pygame.display.flip()
