from chess.notation.forsyth_edwards_notation import Fen, FenChars, iterate
from chess.piece_movement import get_available_moves, get_possible_threats


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


def is_material_insufficient(self) -> bool:
    piece_count: dict[str, int] = {}
    for piece_fen in iterate(self.data.piece_placement):
        if piece_fen == FenChars.BLANK_PIECE.value: continue
        if piece_fen in piece_count:
            piece_count[piece_fen] += 1
        else:
            piece_count[piece_fen] = 0

    # TODO: implement these
    # King vs king
    # King + minor piece (bishop or knight) vs king
    # King + two knights vs king
    # King + minor piece vs king + minor piece
    # Lone king vs all the pieces
    #   - in this case even if the player with all the pieces runs out of time its still a draw

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
