import typing

from chess.notation.forsyth_edwards_notation import Fen
from chess.notation.forsyth_edwards_notation import FenChars
from chess.notation.algebraic_notation import AlgebraicNotation
from config.pg_config import BOARD_SIZE

AvailableMovesGetter: typing.TypeAlias = typing.Callable[[int, Fen, None | bool], list[int]]


class PieceMovement:
    getters: dict[str, AvailableMovesGetter] = {}

    @staticmethod
    def load() -> None:
        PieceMovement.getters[FenChars.DEFAULT_PAWN] = pawn_available_moves
        PieceMovement.getters[FenChars.DEFAULT_KNIGHT] = knight_available_moves
        PieceMovement.getters[FenChars.DEFAULT_ROOK] = rook_available_moves
        PieceMovement.getters[FenChars.DEFAULT_BISHOP] = bishop_available_moves
        PieceMovement.getters[FenChars.DEFAULT_QUEEN] = queen_available_moves
        PieceMovement.getters[FenChars.DEFAULT_KING] = king_available_moves

    @staticmethod
    def available_moves_getter(fen_val: str) -> AvailableMovesGetter:
        if len(PieceMovement.getters) == 0: raise Exception("Pieces info has not been loaded")
        getter = PieceMovement.getters.get(fen_val.upper())
        if getter is None: raise Exception(f"fen value not found {fen_val}")
        return getter


def get_available_moves(piece_index: int, fen: Fen, is_white_turn: None | bool = None) -> list[int]:
    fen_val: str = fen[piece_index]
    if is_white_turn is None: is_white_turn = fen.is_white_turn()
    available_moves = PieceMovement.available_moves_getter(fen_val)(piece_index, fen, is_white_turn)

    if fen_val.upper() == FenChars.DEFAULT_KING:
        return process_king_available_moves(piece_index, is_white_turn, fen, available_moves)
    else:
        return process_regular_available_moves(piece_index, is_white_turn, fen, available_moves)


def is_king_safe(from_index: int, dest_index: int, fen: Fen, is_white_turn: None | bool = None) -> bool:
    if is_white_turn is None: is_white_turn = fen.is_white_turn()
    king_fen = FenChars.get_piece_fen(FenChars.DEFAULT_KING, is_white_turn)

    new_fen = Fen(fen.notation)
    new_fen.make_move(from_index, dest_index, new_fen[from_index], False)

    own_king_indexes = new_fen.get_indexes_for_piece(king_fen)
    own_king_index = -1 if len(own_king_indexes) == 0 else own_king_indexes[0]

    possible_threats = get_possible_threats(own_king_index, new_fen, is_white_turn)

    return len(possible_threats) == 0


def get_possible_threats(piece_index: int, fen: Fen, is_white_turn: bool) -> list[int]:
    if piece_index < 0: return []

    threat_knight_fen = FenChars.get_piece_fen(FenChars.DEFAULT_KNIGHT, not is_white_turn)
    own_king_fen = FenChars.get_piece_fen(FenChars.DEFAULT_KING, is_white_turn)
    opponent_king_fen = FenChars.get_piece_fen(FenChars.DEFAULT_KING, not is_white_turn)

    knight_possible_threats = knight_available_moves(piece_index, fen, is_white_turn)
    rest_possible_threats = queen_available_moves(piece_index, fen, is_white_turn)

    possible_threats: list[int] = []
    for threat_index in knight_possible_threats:
        if fen[threat_index] == threat_knight_fen: possible_threats.append(threat_index)

    for threat_index in rest_possible_threats:
        if fen[threat_index] == FenChars.BLANK_PIECE: continue

        threat_available_moves_getter: AvailableMovesGetter = PieceMovement.available_moves_getter(fen[threat_index])
        threat_possible_moves = threat_available_moves_getter(threat_index, fen, not is_white_turn)

        for move in threat_possible_moves:
            if fen[move] == opponent_king_fen: raise Exception('King should never be in this spot')
            if fen[move] == own_king_fen: possible_threats.append(move)

    return possible_threats


def process_regular_available_moves(from_index: int, is_white_turn: bool,
                                    fen: Fen, available_moves: list[int]) -> list[int]:
    safe_moves = []
    for move in available_moves:
        if is_king_safe(from_index, move, fen, is_white_turn):
            safe_moves.append(move)
    return safe_moves


def process_king_available_moves(from_index: int, is_white_turn: bool,
                                 fen: Fen, available_moves: list[int]) -> list[int]:
    safe_moves = []
    king_side_rook_index = 63 if is_white_turn else 7
    queen_side_rook_index = 56 if is_white_turn else 0
    king_in_between = [61, 62] if is_white_turn else [5, 6]
    queen_in_between = [58, 59] if is_white_turn else [2, 3]
    rook_fen = FenChars.get_piece_fen(FenChars.DEFAULT_ROOK, is_white_turn)
    king_not_in_check = is_king_safe(0, 0, fen, is_white_turn)

    for move in available_moves:
        if move == king_side_rook_index and fen[king_side_rook_index] == rook_fen:
            king_castle = True
            for square in king_in_between:
                if not is_king_safe(from_index, square, fen, is_white_turn): king_castle = False
            if king_castle and king_not_in_check: safe_moves.append(move)
        elif move == queen_side_rook_index and fen[queen_side_rook_index] == rook_fen:
            queen_castle = True
            for square in queen_in_between:
                if not is_king_safe(from_index, square, fen, is_white_turn): queen_castle = False
            if queen_castle and king_not_in_check: safe_moves.append(move)
        else:
            if is_king_safe(from_index, move, fen, is_white_turn): safe_moves.append(move)

    return safe_moves


def pawn_available_moves(from_index: int, fen: Fen, is_white_turn: None | bool = None) -> list[int]:
    if is_white_turn is None: is_white_turn = fen.is_white_turn()
    moves = []
    up = get_fen_offset_index(is_white_turn, from_index, 1, 0)  # up
    double_up = get_fen_offset_index(is_white_turn, from_index, 2, 0)  # up_up
    up_right = get_fen_offset_index(is_white_turn, from_index, 1, 1)  # up_right
    up_left = get_fen_offset_index(is_white_turn, from_index, 1, -1)  # up_left

    double_moves = list(range(48, 56)) if is_white_turn else list(range(8, 16))

    # pawn moves up twice in the first move
    if from_index in double_moves:
        if (double_up and up) and \
                (fen[double_up] == FenChars.BLANK_PIECE) and \
                (fen[up] == FenChars.BLANK_PIECE): moves.append(double_up)

    # en passant move
    if fen.data.en_passant_rights != FenChars.EMPTY_INFO:
        index_offset = BOARD_SIZE if fen.is_white_turn() else BOARD_SIZE * -1
        en_passant_an = AlgebraicNotation(*fen.data.en_passant_rights)
        possible_en_passant = AlgebraicNotation.get_an_from_index(en_passant_an.index + index_offset)
        from_an = AlgebraicNotation.get_an_from_index(from_index)
        if possible_en_passant.rank == from_an.rank:
            if from_index == AlgebraicNotation.get_an_from_index(possible_en_passant.index + 1).index or \
                    from_index == AlgebraicNotation.get_an_from_index(possible_en_passant.index - 1).index:
                move = get_fen_offset_index(is_white_turn, en_passant_an.index, 0, 0)
                if move is not None:
                    moves.append(move)

    if (up is not None) and (fen[up] == FenChars.BLANK_PIECE): moves.append(up)

    for move in [up_right, up_left]:
        if move is None:
            continue
        elif is_white_turn:
            if fen[move].islower(): moves.append(move)
        else:
            if fen[move].isupper(): moves.append(move)

    return moves


def knight_available_moves(from_index: int, fen: Fen, is_white_turn: None | bool = None) -> list[int]:
    if is_white_turn is None: is_white_turn = fen.is_white_turn()
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

    moves += move_piece(moves_offset, from_index, fen, is_white_turn, until_friendly=False)

    return moves


def rook_available_moves(from_index: int, fen: Fen, is_white_turn: None | bool = None) -> list[int]:
    if is_white_turn is None: is_white_turn = fen.is_white_turn()
    moves = []
    up, down, right, left = get_flat_offsets()

    moves += move_piece(left, from_index, fen, is_white_turn)
    moves += move_piece(right, from_index, fen, is_white_turn)
    moves += move_piece(up, from_index, fen, is_white_turn)
    moves += move_piece(down, from_index, fen, is_white_turn)

    return moves


def bishop_available_moves(from_index: int, fen: Fen, is_white_turn: None | bool = None) -> list[int]:
    if is_white_turn is None: is_white_turn = fen.is_white_turn()
    moves = []

    up_right, down_right, up_left, down_left = get_diagonal_offsets()

    moves += move_piece(up_right, from_index, fen, is_white_turn)
    moves += move_piece(down_right, from_index, fen, is_white_turn)
    moves += move_piece(up_left, from_index, fen, is_white_turn)
    moves += move_piece(down_left, from_index, fen, is_white_turn)

    return moves


def queen_available_moves(from_index: int, fen: Fen, is_white_turn: None | bool = None) -> list[int]:
    if is_white_turn is None: is_white_turn = fen.is_white_turn()
    moves = []
    moves += bishop_available_moves(from_index, fen, is_white_turn)
    moves += rook_available_moves(from_index, fen, is_white_turn)
    return moves


def king_available_moves(from_index: int, fen: Fen, is_white_turn: None | bool = None) -> list[int]:
    if is_white_turn is None: is_white_turn = fen.is_white_turn()

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

    king_side_rook_index = 63 if is_white_turn else 7
    queen_side_rook_index = 56 if is_white_turn else 0

    king_in_between = [61, 62] if is_white_turn else [5, 6]
    queen_in_between = [57, 58, 59] if is_white_turn else [1, 2, 3]

    king_fen = FenChars.get_piece_fen(FenChars.DEFAULT_KING, is_white_turn)
    queen_fen = FenChars.get_piece_fen(FenChars.DEFAULT_QUEEN, is_white_turn)
    rook_fen = FenChars.get_piece_fen(FenChars.DEFAULT_ROOK, is_white_turn)

    if king_fen in fen.data.castling_rights and fen[king_side_rook_index] == rook_fen:
        king_castle = True
        for move in king_in_between:
            if fen[move] != FenChars.BLANK_PIECE: king_castle = False
        if king_castle: moves.append(king_side_rook_index)

    if queen_fen in fen.data.castling_rights and fen[queen_side_rook_index] == rook_fen:
        queen_castle = True
        for move in queen_in_between:
            if fen[move] != FenChars.BLANK_PIECE: queen_castle = False
        if queen_castle: moves.append(queen_side_rook_index)

    moves += move_piece(moves_offset, from_index, fen, is_white_turn, until_friendly=False)

    return moves


def get_fen_offset_index(is_white_turn: bool, from_index: int, row_offset: int, col_offset: int) -> int | None:
    row = from_index // BOARD_SIZE
    col = from_index - (row * BOARD_SIZE)
    if is_white_turn:
        row_offset = row_offset * -1
        col_offset = col_offset * -1
    new_row = row + row_offset
    new_col = col + col_offset
    if new_row < 0 or new_row > BOARD_SIZE - 1: return None
    if new_col < 0 or new_col > BOARD_SIZE - 1: return None
    return (new_row * BOARD_SIZE) + new_col


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


def move_piece(
        moves_offset: list[tuple[int, int]],
        from_index: int,
        fen: Fen,
        is_white_turn: bool,
        until_friendly: bool = True
) -> list[int]:
    moves = []
    for offset in moves_offset:
        move = get_fen_offset_index(is_white_turn, from_index, *offset)
        if move is None: continue
        if move == from_index: continue
        if fen[move] == FenChars.BLANK_PIECE:
            moves.append(move)
        elif is_white_turn:
            if fen[move].islower(): moves.append(move)
            if until_friendly: break
        else:
            if fen[move].isupper(): moves.append(move)
            if until_friendly: break
    return moves


def is_pawn_promotion(from_an: AlgebraicNotation, dest_an: AlgebraicNotation, fen: Fen) -> bool:
    pawn_fen = FenChars.get_piece_fen(FenChars.DEFAULT_PAWN, fen.is_white_turn())
    rank = '8' if fen.is_white_turn() else '1'
    if fen[from_an.index] != pawn_fen: return False
    if dest_an.rank != rank: return False
    if dest_an.index not in get_available_moves(from_an.index, fen): return False
    if not is_king_safe(from_an.index,
                        dest_an.index, fen): return False
    return True
