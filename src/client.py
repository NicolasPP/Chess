import _thread as thread
import random
import socket as skt
import sys
import time

import click
import pygame

from chess.player import process_server_command, Player
from chess.notation.forsyth_edwards_notation import Fen
from chess.network.command_manager import CommandManager, Command
from chess.asset.chess_assets import PieceSetAssets, Themes
from chess.network.chess_network import ChessNetwork
from chess.piece_movement import Side, PieceMovement
from chess_logging import set_up_logging
from chess.asset.asset_manager import AssetManager

from config import *

logger = set_up_logging(CLIENT_NAME, CLIENT_LOG_FILE)

prev_time = time.time()
delta_time: float = 0


def server_listener(player: Player, server_socket: skt.socket, match_fen: Fen) -> None:
    with server_socket:
        while True:
            data_b: bytes = server_socket.recv(DATA_SIZE)
            if not data_b: break
            commands = CommandManager.deserialize_command_list_bytes(data_b)
            logger.debug("server sent commands :")
            for command in commands:
                logger.debug(" - %s ", command.name)
                process_server_command(command, match_fen, player)

        logger.debug("server disconnected")
        pygame.event.post(pygame.event.Event(pygame.QUIT))


def update_window_caption(player: Player) -> None:
    if player.game_over:
        pygame.display.set_caption('GAME OVER')
    else:
        pygame.display.set_caption(player.get_window_title())


def get_player(init_info: Command) -> Player:
    side = init_info.info[CommandManager.side]
    time_left = init_info.info[CommandManager.time]
    player_side = Side.WHITE if side == Side.WHITE.name else Side.BLACK
    player = Player(
        side=player_side,
        piece_set=random.choice([PieceSetAssets.NORMAL16x32, PieceSetAssets.NORMAL16x16]),
        scale=SCALE,
        time_left=float(time_left)
    )
    return player


def set_delta_time() -> None:
    global prev_time, delta_time
    now = time.time()
    delta_time = now - prev_time
    prev_time = now


def run_main_loop(server_ip: str) -> None:
    pygame.init()
    window_size = pygame.math.Vector2(WINDOW_SIZE)
    pygame.display.set_mode(window_size)
    AssetManager.load_theme(random.choice((Themes.PLAIN1, Themes.PLAIN2, Themes.PLAIN3, Themes.PLAIN4)))
    PieceMovement.load()

    network = ChessNetwork(server_ip)
    init_info: Command = network.connect()

    player = get_player(init_info)
    match_fen = Fen(init_info.info[CommandManager.fen_notation])

    player.set_to_default_pos(window_size)

    player.update_turn(match_fen)
    player.update_pieces_location(match_fen)

    thread.start_new_thread(server_listener, (player, network.socket, match_fen))
    done = False
    while not done:
        set_delta_time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: done = True
            player.parse_input(event, match_fen, network=network)

        update_window_caption(player)
        player.render()
        player.update(delta_time, network=network)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


@click.command()
@click.option('--server_ip', default='127.0.0.1', help='set the server ip address default = 127.0.0.1')
def start_client(server_ip: str) -> None:
    run_main_loop(server_ip)


if __name__ == '__main__':
    start_client()
