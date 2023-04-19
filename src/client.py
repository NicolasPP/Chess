import _thread as thread
import socket as skt
import sys
import time

import click
import pygame

from chess.chess_player import process_server_command, Player
from chess.notation.forsyth_edwards_notation import Fen
from chess.network.command_manager import CommandManager, Command
from chess.asset.chess_assets import PieceSetAssets, Themes, ChessTheme, PieceSetAsset
from chess.network.chess_network import ChessNetwork
from chess.board.side import Side
from chess.chess_logging import set_up_logging
from chess.chess_init import init_chess
from chess.game.game_surface import GameSurface

from config import *

logger = set_up_logging(CLIENT_NAME, CLIENT_LOG_FILE)

prev_time = time.time()
delta_time: float = 0


def server_listener(player: Player, server_socket: skt.socket, match_fen: Fen) -> None:
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


def set_delta_time() -> None:
    global prev_time, delta_time
    now = time.time()
    delta_time = now - prev_time
    prev_time = now


def run_main_loop(server_ip: str, theme: ChessTheme, scale: float, piece_set: PieceSetAsset) -> None:
    init_chess(theme, piece_set, scale)
    center = GameSurface.get().get_rect(center=pygame.display.get_surface().get_rect().center)

    network = ChessNetwork(server_ip)
    init_info: Command = network.connect()

    player: Player = Player.get_player_client(init_info, center)
    match_fen = Fen(init_info.info[CommandManager.fen_notation])

    player.update_turn(match_fen)
    player.update_pieces_location(match_fen)

    thread.start_new_thread(server_listener, (player, network.socket, match_fen))
    done = False
    while not done:
        set_delta_time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: done = True
            player.parse_input(event, match_fen, network=network)

        player.render()
        player.update(delta_time, network=network)

        pygame.display.get_surface().blit(GameSurface.get(), center)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


@click.command()
@click.option('--server_ip', default='127.0.0.1', help='set the server ip address default = 127.0.0.1')
@click.option('--scale', default=3.5, help='size of chess game, lower than 3.5 will cause the fonts to be unclear')
@click.option('--theme_id', default=1, help='game theme, possible ids (1 - 4), (-1 for random theme)')
@click.option('--pieces_asset', default='RANDOM', help='piece assets, possible names SMALL, LARGE, RANDOM')
def start_client(server_ip: str, scale: float, theme_id: int, pieces_asset: str) -> None:
    run_main_loop(server_ip, Themes.get_theme(theme_id), scale, PieceSetAssets.get_asset(pieces_asset))


if __name__ == '__main__':
    start_client()
