import _thread as thread
import logging
import random
import socket as skt
import sys

import click
import pygame

from chess.player import parse_command, Player
from utils.forsyth_edwards_notation import Fen
from utils.commands import split_command_info
from utils.asset import PieceSetAssets, BoardAssets
from utils.debug import debug
from utils.network import Network
import chess.board as chess_board

from config import *

logging.basicConfig(
    filename='log/client.log',
    encoding='utf-8',
    level=logging.DEBUG,
    filemode='w',
    format='%(asctime)s\t%(levelname)s\t%(message)s'
)


def server_listener(player: Player, server_socket: skt.socket, match_fen: Fen) -> None:
    with server_socket:
        while True:
            data_b: bytes = server_socket.recv(DATA_SIZE)
            if not data_b: break
            prev_data_tail = ''
            data, prev_data_tail = correct_data(data_b.decode('utf-8'), prev_data_tail)
            logging.debug("server sent commands :")
            for command_info in data[:-1].split(C_SPLIT):
                command, info = split_command_info(command_info)
                logging.debug(" - %s ", command)
                logging.debug(" - - %s", info)
                parse_command(command, info, match_fen, player)

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


def get_player(network: Network) -> Player:
    side = chess_board.SIDE.WHITE if network.id % 2 == 0 else chess_board.SIDE.BLACK
    player = Player(
        side=side,
        piece_set=random.choice(list(PieceSetAssets)),
        board_asset=random.choice(list(BoardAssets)),
        scale=BOARD_SCALE)
    return player


def center_board(player: Player, window_size: pygame.math.Vector2) -> None:
    screen_center = window_size / 2
    player.board.pos_rect.center = round(screen_center.x), round(screen_center.y)


def get_colors(player: Player) -> tuple[str, str]:
    bg_color = 'white' if player.side == chess_board.SIDE.WHITE else 'black'
    font_color = 'black' if player.side == chess_board.SIDE.WHITE else 'white'
    return bg_color, font_color


def run_main_loop(server_ip: str) -> None:
    pygame.init()

    window_size = pygame.math.Vector2(WINDOW_SIZE)
    pygame.display.set_mode(window_size)

    clock = pygame.time.Clock()
    network = Network(server_ip)
    game_state = network.read()
    match_fen = Fen(game_state)
    player = get_player(network)
    player.update_turn(match_fen)
    bg_color, font_color = get_colors(player)

    thread.start_new_thread(server_listener, (player, network.socket, match_fen))

    center_board(player, window_size)
    player.update_pieces_location(match_fen)

    done = False
    while not done:

        fps = round(clock.get_fps())

        for event in pygame.event.get():
            if event.type == pygame.QUIT: done = True
            player.parse_input(event, match_fen, network=network)

        update_window_caption(player)
        player.render(bg_color)

        debug(fps, bg_color, font_color)
        pygame.display.flip()
        clock.tick()

    pygame.quit()
    sys.exit()


@click.command()
@click.option('--server_ip', default='127.0.0.1', help='set the server ip address default = 127.0.0.1')
def start_client(server_ip: str) -> None:
    run_main_loop(server_ip)


if __name__ == '__main__':
    start_client()
