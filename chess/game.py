import typing

import chess.chess_data as CHESS
import utils.FEN_notation as FEN
from config import *

# -- Defining Movement --
'''
set_info_for()
will set the individual move set for all the pieces
anything specific to a pieces move set will live in the function
which is wrapped by set_info_for()
'''


def set_info_for(piece: CHESS.PIECES, fen_val: str):
    def set_valid_move(get_valid_moves: typing.Callable):
        piece.set_moves(get_valid_moves)
        piece.set_fen(fen_val)
        return get_valid_moves

    return set_valid_move


@set_info_for(CHESS.PIECES.PAWN, 'P')
def pawn_available_moves(from_index: int, fen: FEN.Fen, is_white_turn: bool) -> list[int]:
    moves = []
    up = get_fen_offset_index(is_white_turn, from_index, 1, 0)  # up
    double_up = get_fen_offset_index(is_white_turn, from_index, 2, 0)  # up_up
    up_right = get_fen_offset_index(is_white_turn, from_index, 1, 1)  # up_right
    up_left = get_fen_offset_index(is_white_turn, from_index, 1, -1)  # up_left

    double_moves = list(range(48, 56)) if is_white_turn else list(range(8, 16))

    # pawn moves up twice in the first move
    if from_index in double_moves:
        if (double_up and up) and \
                (fen[double_up] == FEN.FenChars.BLANK_PIECE.value) and \
                (fen[up] == FEN.FenChars.BLANK_PIECE.value): moves.append(double_up)

    if (up is not None) and (fen[up] == FEN.FenChars.BLANK_PIECE.value): moves.append(up)

    for move in [up_right, up_left]:
        if move is None:
            continue
        elif is_white_turn:
            if fen[move].islower(): moves.append(move)
        else:
            if fen[move].isupper(): moves.append(move)

    return moves


@set_info_for(CHESS.PIECES.KNIGHT, 'N')
def knight_available_moves(from_index: int, fen: FEN.Fen, is_white_turn: bool) -> list[int]:
    moves = []
    moves_offset = [
        (2, -1),  # up_right
        (2, 1),  # up_left
        (1, -2),  # right_up
        (-1, -2),  # right_down
        (-2, -1),  # down_right
        (-2, 1),  # down_left
        (-1, 2),  # left_down
        (1, 2)  # left_up
    ]

    moves += move_fixed_amount(moves_offset, from_index, fen, is_white_turn)

    return moves


@set_info_for(CHESS.PIECES.ROOK, 'R')
def rook_available_moves(from_index: int, fen: FEN.Fen, is_white_turn: bool) -> list[int]:
    moves = []
    up, down, right, left = get_flat_offsets()

    moves += move_until_friendly(left, from_index, fen, is_white_turn)
    moves += move_until_friendly(right, from_index, fen, is_white_turn)
    moves += move_until_friendly(up, from_index, fen, is_white_turn)
    moves += move_until_friendly(down, from_index, fen, is_white_turn)

    return moves


@set_info_for(CHESS.PIECES.BISHOP, 'B')
def bishop_available_moves(from_index: int, fen: FEN.Fen, is_white_turn: bool) -> list[int]:
    moves = []

    up_right, down_right, up_left, down_left = get_diagonal_offsets()

    moves += move_until_friendly(up_right, from_index, fen, is_white_turn)
    moves += move_until_friendly(down_right, from_index, fen, is_white_turn)
    moves += move_until_friendly(up_left, from_index, fen, is_white_turn)
    moves += move_until_friendly(down_left, from_index, fen, is_white_turn)

    return moves


@set_info_for(CHESS.PIECES.QUEEN, 'Q')
def queen_available_moves(from_index: int, fen: FEN.Fen, is_white_turn: bool) -> list[int]:
    moves = []
    moves += bishop_available_moves(from_index, fen, is_white_turn)
    moves += rook_available_moves(from_index, fen, is_white_turn)
    return moves


@set_info_for(CHESS.PIECES.KING, 'K')
def king_available_moves(from_index: int, fen: FEN.Fen, is_white_turn: bool) -> list[int]:
    moves = []
    moves_offset = [
        (1, -1),  # up_right
        (1, 1),  # up_left
        (-1, -1),  # down_right
        (-1, 1),  # down_left
        (1, 0),  # up
        (0, -1),  # right
        (-1, 0),  # down
        (0, 1),  # left
    ]

    moves += move_fixed_amount(moves_offset, from_index, fen, is_white_turn)

    return moves


# -----------------------


# -- Piece Move Helpers --


def get_available_moves(piece_name: str, from_index: int, fen: FEN.Fen, is_white_turn: bool) -> list[int]:
    available_moves = CHESS.PIECES[piece_name].available_moves(from_index, fen, is_white_turn)
    safe_moves = []
    for move in available_moves:
        if is_king_safe(from_index, move, fen, is_white_turn): safe_moves.append(move)
    return safe_moves


def get_fen_offset_index(is_white_turn: bool, from_index: int, row_offset: int, col_offset: int) -> int | None:
    row, col = get_fen_row_col(from_index)
    if is_white_turn:
        row_offset = row_offset * -1
        col_offset = col_offset * -1
    new_row = row + row_offset
    new_col = col + col_offset
    if new_row < 0 or new_row > BOARD_SIZE - 1: return None
    if new_col < 0 or new_col > BOARD_SIZE - 1: return None
    return (new_row * BOARD_SIZE) + new_col


def get_fen_row_col(index: int) -> tuple[int, int]:
    row = index // BOARD_SIZE
    col = index - (row * BOARD_SIZE)
    return row, col


def get_diagonal_offsets(
) -> tuple[list[tuple[int, int]], list[tuple[int, int]], list[tuple[int, int]], list[tuple[int, int]]]:
    up_right = [(index, -index) for index in range(BOARD_SIZE)]
    down_right = [(-index, -index) for index in range(BOARD_SIZE)]
    up_left = [(index, index) for index in range(BOARD_SIZE)]
    down_left = [(-index, index) for index in range(BOARD_SIZE)]
    return up_right, down_right, up_left, down_left


def get_flat_offsets(
) -> tuple[list[tuple[int, int]], list[tuple[int, int]], list[tuple[int, int]], list[tuple[int, int]]]:
    left = [(0, index) for index in range(BOARD_SIZE)]
    right = [(0, -index) for index in range(BOARD_SIZE)]
    up = [(index, 0) for index in range(BOARD_SIZE)]
    down = [(-index, 0) for index in range(BOARD_SIZE)]
    return up, down, right, left


def move_until_friendly(
        moves_offset: list[tuple[int, int]],
        from_index: int,
        fen: FEN.Fen,
        is_white_turn: bool
) -> list[int]:
    moves = []
    for offset in moves_offset:
        move = get_fen_offset_index(is_white_turn, from_index, *offset)
        if move is None: continue
        if move == from_index: continue
        if fen[move] == FEN.FenChars.BLANK_PIECE.value:
            moves.append(move)
        elif is_white_turn:
            if fen[move].islower(): moves.append(move)
            break
        else:
            if fen[move].isupper(): moves.append(move)
            break
    return moves


def move_fixed_amount(
        moves_offset: list[tuple[int, int]],
        from_index: int,
        fen: FEN.Fen,
        is_white_turn: bool
) -> list[int]:
    moves = []
    for offset in moves_offset:
        move = get_fen_offset_index(is_white_turn, from_index, *offset)
        if move is None: continue
        if fen[move] == FEN.FenChars.BLANK_PIECE.value:
            moves.append(move)
        elif is_white_turn:
            if fen[move].islower(): moves.append(move)
        else:
            if fen[move].isupper(): moves.append(move)
    return moves


# ------------------------

# -- Checking if Move is Valid --


def is_move_valid(from_index: int, dest_index: int, fen: FEN.Fen, is_white_turn: bool) -> bool:
    if not is_from_valid(fen[from_index], is_white_turn): return False
    if not is_side_valid(from_index, dest_index, fen): return False
    if not is_destination_valid(from_index, dest_index, fen, is_white_turn): return False
    return True


# -- helpers --


def is_check(fen: FEN.Fen, is_white_turn: bool) -> bool:
    own_moves = get_own_available_moves(fen, is_white_turn, use_getter=True)
    king_fen = 'k' if is_white_turn else 'K'
    for move in own_moves:
        if fen[move] == king_fen: return True
    return False


def is_checkmate(fen: FEN.Fen, is_white_turn: bool) -> bool:
    opponents_moves = get_opponent_available_moves(fen, is_white_turn, use_getter=True)
    return len(opponents_moves) == 0


def get_own_available_moves(fen: FEN.Fen, is_white_turn: bool, use_getter: bool = False) -> list[int]:
    moves = []
    for index, fen_char in enumerate(fen.expanded):
        if fen_char == FEN.FenChars.BLANK_PIECE.value: continue
        if not is_same_side(is_white_turn, fen_char): continue
        piece_name = CHESS.get_name_from_fen(fen_char)
        if use_getter:
            moves += get_available_moves(piece_name, index, fen, is_white_turn)
        else:
            moves += CHESS.PIECES[piece_name].available_moves(index, fen, is_white_turn)
    return moves


def get_opponent_available_moves(fen: FEN.Fen, is_white_turn: bool, use_getter: bool = False) -> list[int]:
    moves = []
    for index, fen_char in enumerate(fen.expanded):
        if fen_char == FEN.FenChars.BLANK_PIECE.value: continue
        if is_same_side(is_white_turn, fen_char): continue
        piece_name = CHESS.get_name_from_fen(fen_char)
        if use_getter:
            moves += get_available_moves(piece_name, index, fen, not is_white_turn)
        else:
            moves += CHESS.PIECES[piece_name].available_moves(index, fen, not is_white_turn)
    return moves


def is_same_side(is_white_turn: bool, fen_char: str) -> bool:
    return (is_white_turn and fen_char.isupper()) if is_white_turn else ((not is_white_turn) and fen_char.islower())


def is_from_valid(from_fen_val: str, is_white_turn: bool) -> bool:
    if from_fen_val == FEN.FenChars.BLANK_PIECE.value: return False
    if not is_from_correct_side(from_fen_val, is_white_turn): return False
    return True


def is_side_valid(from_index: int, dest_index: int, fen: FEN.Fen) -> bool:
    if is_same(from_index, dest_index): return False
    if is_same_team(fen[from_index], fen[dest_index]): return False
    return True


def is_destination_valid(from_index: int, dest_index: int, fen: FEN.Fen, is_white_turn: bool) -> bool:
    piece_name = CHESS.get_name_from_fen(fen[from_index])
    available_moves = get_available_moves(piece_name, from_index, fen, is_white_turn)
    if dest_index not in available_moves: return False
    return True


def is_king_safe(from_index: int, dest_index: int, fen: FEN.Fen, is_white_turn: bool) -> bool:
    new_fen = FEN.Fen(fen.get_notation())
    king_fen = 'K' if is_white_turn else 'k'

    new_fen.make_move(from_index, dest_index)

    for move in get_opponent_available_moves(new_fen, is_white_turn):
        if new_fen[move] == king_fen: return False

    return True


def is_from_correct_side(from_fen_val: str, is_white: bool) -> bool:
    if is_white: return from_fen_val.isupper()
    return from_fen_val.islower()


def is_same(from_index: int, dest_index: int) -> bool:
    return from_index == dest_index


def is_same_team(piece1: str, piece2: str) -> bool:
    if piece2 == FEN.FenChars.BLANK_PIECE.value: return False
    return piece1.islower() == piece2.islower()
# -------------------------------
