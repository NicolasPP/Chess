from chess.notation.forsyth_edwards_notation import Fen, FenChars, InsufficientMaterialInfo
from chess.movement.piece_movement import get_available_moves, get_possible_threats


def is_move_valid(from_index: int, dest_index: int, fen: Fen) -> bool:
    if not is_from_valid(fen, from_index): return False
    if not is_side_valid(from_index, dest_index, fen): return False
    if not is_destination_valid(from_index, dest_index, fen): return False
    return True


def is_check(fen: Fen, is_white_turn: None | bool = None) -> bool:
    if is_white_turn is None: is_white_turn = fen.is_white_turn()
    king_fen = FenChars.DEFAULT_KING.get_piece_fen(is_white_turn)
    king_index = fen.get_indexes_for_piece(king_fen)
    threats = get_possible_threats(king_index[0], fen, is_white_turn)
    return len(threats) != 0


def is_checkmate(fen: Fen, is_white_turn: None | bool = None) -> bool:
    if is_white_turn is None: is_white_turn = fen.is_white_turn()
    all_moves = get_all_available_moves(fen, is_white_turn, own_moves=True)
    return len(all_moves) == 0 and is_check(fen, is_white_turn)


def is_take(fen: Fen, dest_index: int, is_en_passant: bool, is_castle: bool) -> bool:
    if is_castle: return False
    return (fen[dest_index] != FenChars.BLANK_PIECE.value) or is_en_passant


def get_all_available_moves(fen: Fen, is_white_turn: None | bool = None, *, own_moves: bool) -> list[int]:
    moves = []
    if is_white_turn is None: is_white_turn = fen.is_white_turn()
    for index, fen_char in enumerate(fen.expanded):
        same_side = is_same_side(is_white_turn, fen_char)
        if fen_char == FenChars.BLANK_PIECE.value: continue
        if not same_side if own_moves else same_side: continue

        moves += get_available_moves(fen_char, index, fen, own_moves == is_white_turn)

    return moves


def is_stale_mate(fen: Fen) -> bool:
    if is_check(fen, not fen.is_white_turn()) or is_check(fen, fen.is_white_turn()): return False
    own_moves = get_all_available_moves(fen, own_moves=True)
    opp_moves = get_all_available_moves(fen, not fen.is_white_turn(), own_moves=True)
    if len(own_moves) != 0 and len(opp_moves) != 0: return False
    return True


def is_material_insufficient(fen: Fen) -> bool:
    imi: InsufficientMaterialInfo = fen.get_insufficient_material_info()
    minor_piece_count: int = len(imi.minor_pieces)
    # https://www.chess.com/article/view/how-chess-games-can-end-8-ways-explained#insufficient-material
    # pawns on the board:
    if any(imi.is_pawn_present):
        return False

    # King vs king
    if imi.total_count == 2:
        return True

    # King + minor piece vs king
    if imi.total_count == 3 and minor_piece_count == 1:
        return True

    if imi.total_count == 4 and minor_piece_count == 2:
        white_knight = FenChars.DEFAULT_KNIGHT.get_piece_fen(True)
        black_knight = FenChars.DEFAULT_KNIGHT.get_piece_fen(False)
        first_p, second_p = imi.minor_pieces
        if first_p != second_p:
            # King + minor piece vs king + minor piece
            if not (first_p.isupper() and second_p.isupper()):
                return True

        else:
            # King + two knights vs king
            if first_p == white_knight or first_p == black_knight:
                return True

    return False


def is_same_side(is_white_turn: bool, fen_char: str) -> bool:
    return (is_white_turn and fen_char.isupper()) if is_white_turn else ((not is_white_turn) and fen_char.islower())


def is_from_valid(fen: Fen, from_index: int) -> bool:
    from_fen_val = fen[from_index]
    if from_fen_val == FenChars.BLANK_PIECE.value: return False
    if not is_from_correct_side(from_fen_val, fen.is_white_turn()): return False
    return True


def is_side_valid(from_index: int, dest_index: int, fen: Fen) -> bool:
    if fen.is_move_castle(from_index, dest_index): return True
    if from_index == dest_index: return False
    if is_same_team(fen[from_index], fen[dest_index]): return False
    return True


def is_destination_valid(from_index: int, dest_index: int, fen: Fen) -> bool:
    available_moves = get_available_moves(fen[from_index], from_index, fen)
    if dest_index not in available_moves: return False
    return True


def is_from_correct_side(from_fen_val: str, is_white: bool) -> bool:
    if is_white: return from_fen_val.isupper()
    return from_fen_val.islower()


def is_same_team(piece1: str, piece2: str) -> bool:
    if piece2 == FenChars.BLANK_PIECE.value: return False
    return piece1.islower() == piece2.islower()
