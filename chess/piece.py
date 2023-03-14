from __future__ import annotations

import dataclasses
import enum
import typing

import utils.asset as ASSETS
import utils.Forsyth_Edwards_notation as FEN
import chess.piece_movement as movement

AvailableMovesGetter: typing.TypeAlias = typing.Callable[[int, FEN.Fen, None | bool], list[int]]


class PieceName(enum.Enum):
    PAWN: str = "P"
    KNIGHT: str = "N"
    ROOK: str = "R"
    BISHOP: str = "B"
    QUEEN: str = "Q"
    KING: str = "K"


@dataclasses.dataclass
class PieceInfo:
    asset_index: int
    piece_name: PieceName
    available_moves: AvailableMovesGetter


class Pieces:
    sprites: dict[str, ASSETS.Sprite] = {}
    info: dict[str, PieceInfo] = {}

    @staticmethod
    def load_pieces_sprites(piece_set: ASSETS.PieceSet, scale: float):
        white_sprites, black_sprites = ASSETS.load_piece_set(piece_set, scale)
        assert len(white_sprites) == len(black_sprites)
        for fen_value, piece_info in Pieces.info.items():
            Pieces.sprites[fen_value.upper()] = white_sprites[piece_info.asset_index]  # White
            Pieces.sprites[fen_value.lower()] = black_sprites[piece_info.asset_index]  # Black

    @staticmethod
    def load_pieces_info():
        Pieces.info[PieceName.PAWN.value] = PieceInfo(0, PieceName.PAWN, movement.pawn_available_moves)
        Pieces.info[PieceName.KNIGHT.value] = PieceInfo(1, PieceName.KNIGHT, movement.knight_available_moves)
        Pieces.info[PieceName.ROOK.value] = PieceInfo(2, PieceName.ROOK, movement.rook_available_moves)
        Pieces.info[PieceName.BISHOP.value] = PieceInfo(3, PieceName.BISHOP, movement.bishop_available_moves)
        Pieces.info[PieceName.QUEEN.value] = PieceInfo(4, PieceName.QUEEN, movement.queen_available_moves)
        Pieces.info[PieceName.KING.value] = PieceInfo(5, PieceName.KING, movement.king_available_moves)

    @staticmethod
    def load(piece_set: ASSETS.PieceSet, scale: float) -> None:
        Pieces.load_pieces_info()
        Pieces.load_pieces_sprites(piece_set, scale)

    @staticmethod
    def get_info_from_fen(fen_val: str) -> PieceInfo:
        info = Pieces.info.get(fen_val.upper())
        if len(Pieces.info) == 0: raise Exception("Pieces info has not been loaded")
        if info is None: raise Exception(f"fen value not found {fen_val}")
        return info


def get_available_moves(fen_val: str, from_index: int, fen: FEN.Fen, is_white_turn: None | bool = None) -> list[int]:
    if is_white_turn is None: is_white_turn = fen.is_white_turn()
    available_moves = Pieces.get_info_from_fen(fen_val).available_moves(from_index, fen, is_white_turn)

    if fen_val.upper() == PieceName.KING.value:
        return process_king_available_moves(from_index, is_white_turn, fen, available_moves)
    else:
        return process_regular_available_moves(from_index, is_white_turn, fen, available_moves)


def is_king_safe(from_index: int, dest_index: int, fen: FEN.Fen, is_white_turn: None | bool = None) -> bool:
    if is_white_turn is None: is_white_turn = fen.is_white_turn()
    king_fen = FEN.FenChars.WHITE_KING.value if is_white_turn else FEN.FenChars.BLACK_KING.value

    new_fen = FEN.Fen(fen.notation)
    new_fen.make_move(from_index, dest_index, new_fen[from_index])

    own_king_indexes = new_fen.get_indexes_for_piece(king_fen)
    own_king_index = -1 if len(own_king_indexes) == 0 else own_king_indexes[0]

    possible_threats = get_possible_threats(own_king_index, new_fen, is_white_turn)

    return len(possible_threats) == 0


def get_possible_threats(piece_index: int, fen: FEN.Fen, is_white_turn: bool) -> list[int]:
    if piece_index < 0: return []
    threat_knight_fen = FEN.FenChars.BLACK_KNIGHT.value if is_white_turn else FEN.FenChars.WHITE_KNIGHT.value
    own_king_fen = FEN.FenChars.WHITE_KING.value if is_white_turn else FEN.FenChars.BLACK_KING.value
    opponent_king_fen = FEN.FenChars.BLACK_KING.value if is_white_turn else FEN.FenChars.WHITE_KING.value

    knight_possible_threats = movement.knight_available_moves(piece_index, fen, is_white_turn)
    rest_possible_threats = movement.queen_available_moves(piece_index, fen, is_white_turn)

    possible_threats: list[int] = []
    for threat_index in knight_possible_threats:
        if fen[threat_index] is threat_knight_fen: possible_threats.append(threat_index)

    for threat_index in rest_possible_threats:
        if fen[threat_index] is FEN.FenChars.BLANK_PIECE.value: continue

        threat_info = Pieces.get_info_from_fen(fen[threat_index])
        threat_possible_moves = threat_info.available_moves(threat_index, fen, not is_white_turn)

        for move in threat_possible_moves:
            if fen[move] is opponent_king_fen: raise Exception('King should never be in this spot')
            if fen[move] is own_king_fen: possible_threats.append(move)

    return possible_threats


def process_regular_available_moves(from_index: int, is_white_turn: bool, fen: FEN.Fen, available_moves: list[int]) -> \
        list[int]:
    safe_moves = []
    for move in available_moves:
        if is_king_safe(from_index, move, fen, is_white_turn):
            safe_moves.append(move)
    return safe_moves


def process_king_available_moves(from_index: int, is_white_turn: bool, fen: FEN.Fen, available_moves: list[int]) -> \
        list[int]:
    safe_moves = []
    king_side_rook_index = 63 if is_white_turn else 7
    queen_side_rook_index = 56 if is_white_turn else 0
    king_in_between = [61, 62] if is_white_turn else [5, 6]
    queen_in_between = [58, 59] if is_white_turn else [2, 3]
    rook_fen = FEN.FenChars.WHITE_ROOK.value if is_white_turn else FEN.FenChars.BLACK_ROOK.value
    king_not_in_check = is_king_safe(0, 0, fen, is_white_turn)

    for move in available_moves:
        if move == king_side_rook_index and fen[king_side_rook_index] is rook_fen:
            king_castle = True
            for square in king_in_between:
                if not is_king_safe(from_index, square, fen, is_white_turn): king_castle = False
            if king_castle and king_not_in_check: safe_moves.append(move)
        elif move == queen_side_rook_index and fen[queen_side_rook_index] is rook_fen:
            queen_castle = True
            for square in queen_in_between:
                if not is_king_safe(from_index, square, fen, is_white_turn): queen_castle = False
            if queen_castle and king_not_in_check: safe_moves.append(move)
        else:
            if is_king_safe(from_index, move, fen, is_white_turn): safe_moves.append(move)

    return safe_moves
