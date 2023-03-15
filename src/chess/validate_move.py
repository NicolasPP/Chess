import src.utils.forsyth_edwards_notation as notation
import src.chess.piece as chess_piece


def is_move_valid(from_index: int, dest_index: int, fen: notation.Fen) -> bool:
    if not is_from_valid(fen, from_index): return False
    if not is_side_valid(from_index, dest_index, fen): return False
    if not is_destination_valid(from_index, dest_index, fen): return False
    return True


def is_opponent_in_check(fen: notation.Fen, is_white_turn: None | bool = None) -> bool:
    if is_white_turn is None: is_white_turn = fen.is_white_turn()
    opponent_king_fen = notation.FenChars.DEFAULT_KING.get_piece_fen(not is_white_turn)
    opponents_king_index = fen.get_indexes_for_piece(opponent_king_fen)
    threats = chess_piece.get_possible_threats(opponents_king_index[0], fen, not is_white_turn)
    return len(threats) != 0


def is_opponent_in_checkmate(fen: notation.Fen) -> bool:
    opponents_moves = get_all_available_moves(fen, not fen.is_white_turn(), own_moves=False)
    return len(opponents_moves) == 0


def is_take(fen: notation.Fen, dest_index: int, is_en_passant: bool, is_castle: bool) -> bool:
    if is_castle: return False
    return (fen[dest_index] != notation.FenChars.BLANK_PIECE.value) or is_en_passant


def get_all_available_moves(fen: notation.Fen, is_white_turn: None | bool = None, *, own_moves: bool) -> list[int]:
    moves = []
    if is_white_turn is None: is_white_turn = fen.is_white_turn()
    for index, fen_char in enumerate(fen.expanded):
        same_side = is_same_side(is_white_turn, fen_char)
        if fen_char == notation.FenChars.BLANK_PIECE.value: continue
        if not same_side if own_moves else same_side: continue

        moves += chess_piece.get_available_moves(fen_char, index, fen, own_moves == is_white_turn)

    return moves


def is_same_side(is_white_turn: bool, fen_char: str) -> bool:
    return (is_white_turn and fen_char.isupper()) if is_white_turn else ((not is_white_turn) and fen_char.islower())


def is_from_valid(fen: notation.Fen, from_index: int) -> bool:
    from_fen_val = fen[from_index]
    if from_fen_val == notation.FenChars.BLANK_PIECE.value: return False
    if not is_from_correct_side(from_fen_val, fen.is_white_turn()): return False
    return True


def is_side_valid(from_index: int, dest_index: int, fen: notation.Fen) -> bool:
    if fen.is_move_castle(from_index, dest_index): return True
    if from_index == dest_index: return False
    if is_same_team(fen[from_index], fen[dest_index]): return False
    return True


def is_destination_valid(from_index: int, dest_index: int, fen: notation.Fen) -> bool:
    available_moves = chess_piece.get_available_moves(fen[from_index], from_index, fen)
    if dest_index not in available_moves: return False
    return True


def is_from_correct_side(from_fen_val: str, is_white: bool) -> bool:
    if is_white: return from_fen_val.isupper()
    return from_fen_val.islower()


def is_same_team(piece1: str, piece2: str) -> bool:
    if piece2 == notation.FenChars.BLANK_PIECE.value: return False
    return piece1.islower() == piece2.islower()
