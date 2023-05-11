import _thread as thread
import socket as skt
import sys
import time

import pygame

from chess.chess_player import process_server_command, Player
from chess.notation.forsyth_edwards_notation import Fen
from chess.network.command_manager import CommandManager, Command
from chess.asset.chess_assets import ChessTheme, PieceSetAsset
from chess.network.chess_network import ChessNetwork
from chess.chess_logging import set_up_logging
from chess.chess_init import init_chess
from chess.game.game_surface import GameSurface

from config.pg_config import *


class OnlineLauncher:

    def __init__(self) -> None:
        self.logger = set_up_logging(CLIENT_NAME, CLIENT_LOG_FILE)
        self.prev_time = time.time()
        self.delta_time: float = 0

    def set_delta_time(self) -> None:
        now = time.time()
        self.delta_time = now - self.prev_time
        self.prev_time = now

    def launch(self, server_ip: str, theme: ChessTheme, scale: float, piece_set: PieceSetAsset) -> None:
        init_chess(theme, piece_set, scale)
        center = GameSurface.get().get_rect(center=pygame.display.get_surface().get_rect().center)

        network = ChessNetwork(server_ip)
        init_info: Command = network.connect()

        player: Player = Player.get_player_client(init_info, center)
        match_fen = Fen(init_info.info[CommandManager.fen_notation])

        player.update_turn(match_fen)
        player.update_pieces_location(match_fen)

        thread.start_new_thread(server_listener, (player, network.socket, match_fen, self.logger))
        done = False
        while not done:
            self.set_delta_time()

            for event in pygame.event.get():
                if event.type == pygame.QUIT: done = True
                player.parse_input(event, match_fen, network=network)

            player.render()
            player.update(self.delta_time, network=network)

            pygame.display.get_surface().blit(GameSurface.get(), center)
            pygame.display.flip()

        pygame.quit()
        sys.exit()


def server_listener(player: Player, server_socket: skt.socket, match_fen: Fen, logger) -> None:
    with server_socket:
        while True:
            data_b: bytes | None = None
            try:
                data_b = server_socket.recv(DATA_SIZE)
            except ConnectionResetError as e:
                logger.debug("%s", e)
            if not data_b: break
            commands = CommandManager.deserialize_command_list_bytes(data_b)
            logger.debug("server sent commands :")
            for command in commands:
                logger.debug(" - %s ", command.name)
                process_server_command(command, match_fen, player)

        logger.debug("server disconnected")
        return


