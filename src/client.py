import _thread as thread
import logging
import random
import socket as skt
import sys
import time

import click
import pygame

from chess.player import parse_command, Player
from utils.forsyth_edwards_notation import Fen
from utils.command_manager import CommandManager, Command
from utils.asset import PieceSetAssets, BoardAssets
from utils.network import ChessNetwork
from chess.piece_movement import Side

from config import *

logging.basicConfig(
    filename='../Chess/log/client.log',
    encoding='utf-8',
    level=logging.DEBUG,
    filemode='w',
    format='%(asctime)s\t%(levelname)s\t%(message)s'
)

prev_time = time.time()
delta_time: float = 0


def server_listener(player: Player, server_socket: skt.socket, match_fen: Fen) -> None:
    with server_socket:
        while True:
            data_b: bytes = server_socket.recv(DATA_SIZE)
            if not data_b: break
            commands = CommandManager.deserialize_command_list_bytes(data_b)
            logging.debug("server sent commands :")
            for command in commands:
                logging.debug(" - %s ", command.name)
                parse_command(command, match_fen, player)

        logging.debug("server disconnected")


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
        board_asset=random.choice(list(BoardAssets)),
        scale=BOARD_SCALE,
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
        player.update(delta_time)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


@click.command()
@click.option('--server_ip', default='127.0.0.1', help='set the server ip address default = 127.0.0.1')
def start_client(server_ip: str) -> None:
    run_main_loop(server_ip)


if __name__ == '__main__':
    start_client()
