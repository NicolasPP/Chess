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
# from utils.commands import split_command_info
from utils.command_manager import CommandManager
from utils.asset import PieceSetAssets, BoardAssets
from utils.network import ChessNetwork, ClientInitInfo
import chess.board as chess_board

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
            # prev_data_tail = ''
            # data, prev_data_tail = correct_data(data_b.decode('utf-8'), prev_data_tail)
            logging.debug("server sent commands :")
            for command in commands:
                logging.debug(" - %s ", command)
                # print(command.name)
                # print(command.info)
                parse_command(command, match_fen, player)

        logging.debug("server disconnected")


def correct_data(received_data: str, prev_data_tail: str) -> tuple[str, str]:
    last_char = received_data[-1]
    temp_data = received_data.split(END_MARKER)

    if temp_data[-1] == '': temp_data = temp_data[:-1]

    if last_char != END_MARKER:
        prev_data_tail = temp_data[-1]
        temp_data = temp_data[:-1]
        logging.debug("Data is incomplete, Tail : %s", prev_data_tail)
        logging.debug("Last correct pair : %s", temp_data[-1])

    return temp_data[-1], prev_data_tail


def update_window_caption(player: Player) -> None:
    if player.game_over:
        pygame.display.set_caption('GAME OVER')
    else:
        pygame.display.set_caption(player.get_window_title())


def get_player(init_info: ClientInitInfo) -> Player:
    side = chess_board.SIDE.WHITE if init_info.side == chess_board.SIDE.WHITE.name else chess_board.SIDE.BLACK
    player = Player(
        side=side,
        piece_set=random.choice([PieceSetAssets.NORMAL16x32, PieceSetAssets.NORMAL16x16]),
        board_asset=random.choice(list(BoardAssets)),
        scale=BOARD_SCALE,
        time_left=float(init_info.time_left)
    )
    return player


def get_colors(player: Player) -> tuple[str, str]:
    bg_color = 'white' if player.side == chess_board.SIDE.WHITE else 'black'
    fg_color = 'black' if player.side == chess_board.SIDE.WHITE else 'white'
    return bg_color, fg_color


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
    init_info: ClientInitInfo = network.connect()

    player = get_player(init_info)
    match_fen = Fen(init_info.fen_str)

    bg_color, fg_color = get_colors(player)
    player.center_board(window_size)

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
        player.render(fg_color, bg_color)
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
