import dataclasses
import enum
import typing

import utils.algebraic_notation as AN
from config import *


class FenChars(enum.Enum):
    BLANK_PIECE: str = "@"
    SPLIT: str = '/'


@dataclasses.dataclass
class FenData:
    piece_placement: str
    active_color: str
    castling_rights: str
    en_passant_rights: str
    half_move_clock: str
    full_move_number: str


class Fen:
    def __init__(self, fen_notation: str = GAME_START_FEN):
        self._notation: str
        self.data: FenData = decode_fen_notation(fen_notation)

        self.expanded: list[str] = self.get_expanded()

    def __getitem__(self, index: int) -> str:
        if index < 0: raise IndexError("no negative index")
        return self.expanded[index]

    def __setitem__(self, index: int, fen_val: str) -> None:
        if index < 0: raise IndexError("no negative index")
        validate_fen_val(fen_val, True)
        self.expanded[index] = fen_val

    def __str__(self):
        return 'fen : ' + self.data.piece_placement + '\n' + self.__repr__()

    def __repr__(self):
        result = ''
        for index, fen_val in enumerate(self.expanded):
            if index % BOARD_SIZE == 0 and index != 0: result += '\n'
            result += fen_val
        return result

    @property
    def notation(self) -> str:
        return encode_fen_data(self.data)

    @notation.setter
    def notation(self, new_notation) -> None:
        self._notation = new_notation

    @notation.deleter
    def notation(self) -> None:
        del self._notation

    def is_white_turn(self) -> bool:
        return self.data.active_color == 'w'

    def get_next_active_color(self) -> str:
        if self.is_white_turn():
            active_color = 'b'
        else:
            active_color = 'w'
        validate_fen_active_color(active_color)
        return active_color

    def get_castling_rights(self, from_piece_val: str, from_index: int) -> str:
        if self.data.castling_rights == '-': return self.data.castling_rights
        castling_rights = self.data.castling_rights
        is_white_turn = True if self.data.active_color == 'w' else False
        king_side_rook_index = 63 if is_white_turn else 7
        queen_side_rook_index = 56 if is_white_turn else 0
        king_index = 60 if is_white_turn else 4
        king_fen = 'K' if is_white_turn else 'k'
        queen_fen = 'Q' if is_white_turn else 'q'
        rook_fen = 'R' if is_white_turn else 'r'
        if from_piece_val == rook_fen:
            if from_index == king_side_rook_index:
                castling_rights = castling_rights.replace(king_fen, '')
            elif from_index == queen_side_rook_index:
                castling_rights = castling_rights.replace(queen_fen, '')

        elif from_piece_val == king_fen and from_index == king_index:
            castling_rights = castling_rights.replace(king_fen, '')
            castling_rights = castling_rights.replace(queen_fen, '')

        if len(castling_rights) == 0: return '-'
        validate_fen_castling_rights(castling_rights)
        return castling_rights

    def get_en_passant_rights(self, from_piece_val: str, from_index: int, dest_index: int) -> str:
        is_white_turn = True if self.data.active_color == 'w' else False
        pawn_fen = 'P' if is_white_turn else 'p'

        double_moves_start = list(range(48, 56)) if is_white_turn else list(range(8, 16))
        double_moves_end = list(range(32, 40)) if is_white_turn else list(range(24, 32))
        if from_piece_val is not pawn_fen: return '-'
        if from_index not in double_moves_start: return '-'
        if dest_index not in double_moves_end: return '-'

        en_passant_rights = AN.get_an_from_index(dest_index).data.coordinates
        validate_fen_en_passant_rights(en_passant_rights)

        return en_passant_rights

    def get_half_move_clock(self, from_piece_val: str, dest_piece_val: str) -> str:
        is_white_turn = True if self.data.active_color == 'w' else False
        pawn_fen = 'P' if is_white_turn else 'p'
        if from_piece_val is pawn_fen or \
                dest_piece_val is not FenChars.BLANK_PIECE.value: return '0'
        half_move_clock = str(int(self.data.half_move_clock) + 1)
        validate_fen_half_move_clock(half_move_clock)
        return half_move_clock

    def get_full_move_number(self) -> str:
        if self.data.active_color == 'w' and \
                self.data.full_move_number == 1:
            return self.data.full_move_number
        full_move_number = str(int(self.data.full_move_number) + 1)
        validate_fen_full_move_number(full_move_number)
        return full_move_number

    def get_expanded(self) -> list[str]:
        expanded_fen: str = ''
        for piece_fen in iterate(self.data.piece_placement):
            if piece_fen.isnumeric():
                expanded_fen += (int(piece_fen) * FenChars.BLANK_PIECE.value)
            elif piece_fen == FenChars.SPLIT.value:
                continue
            else:
                expanded_fen += piece_fen

        return list(expanded_fen)

    def get_index_for_piece(self, piece_fen_val: str) -> list[int]:
        validate_fen_val(piece_fen_val)
        result = []
        for index, fen_val in enumerate(self.expanded):
            if fen_val is piece_fen_val: result.append(index)
        return result

    def get_packed(self) -> str:
        blank_count = 0
        fen_notation, fen_row = [], ''
        for index, fen_val in enumerate(self.expanded):
            if fen_val == FenChars.BLANK_PIECE.value:
                blank_count += 1
                if blank_count == 8:
                    fen_row += str(blank_count)
                    blank_count = 0
            else:
                if blank_count > 0: fen_row += str(blank_count)
                fen_row += fen_val
                blank_count = 0

            if (index + 1) % 8 == 0:
                if blank_count > 0: fen_row += str(blank_count)
                fen_notation.append(fen_row)
                fen_row = ''
                blank_count = 0
        packed = '/'.join(fen_notation)
        validate_fen_piece_placement(packed)
        return packed

    def make_move(self, from_index: int, dest_index: int) -> None:
        from_piece_val = self[from_index]
        dest_piece_val = self[dest_index]

        self[dest_index] = self[from_index]
        self[from_index] = FenChars.BLANK_PIECE.value

        self.data.piece_placement = self.get_packed()
        self.data.castling_rights = self.get_castling_rights(from_piece_val, from_index)
        self.data.en_passant_rights = self.get_en_passant_rights(from_piece_val, from_index, dest_index)
        self.data.half_move_clock = self.get_half_move_clock(from_piece_val, dest_piece_val)
        self.data.full_move_number = self.get_full_move_number()
        self.data.active_color = self.get_next_active_color()


# -- Helpers --
def iterate(piece_placement: str) -> typing.Generator[str, None, None]:
    for fen_row in piece_placement.split(FenChars.SPLIT.value):
        for piece_fen in fen_row: yield piece_fen


def validate_fen_piece_placement(piece_placement) -> bool:
    count = 0
    for piece_fen in iterate(piece_placement):
        if piece_fen.isnumeric():
            int_fen = int(piece_fen)
            if int_fen == 0: raise Exception('INVALID fen notation: number too small')
            if int_fen > 8: raise Exception('INVALID fen notation: number too big')
            count += int_fen
        else:
            validate_fen_val(piece_fen)
            count += 1
    assert count == 64, "INVALID fen notation: too many or too few"
    return True


def validate_fen_val(fen_val: str, expanded_vals: bool = False) -> bool:
    possible_vals = ['p', 'P', 'b', 'B', 'k', 'K', 'n', 'N', 'q', 'Q', 'r', 'R']
    if expanded_vals: possible_vals.append(FenChars.BLANK_PIECE.value)
    if fen_val not in possible_vals:
        raise Exception('INVALID fen notation: invalid fen val')
    return True


def validate_fen_active_color(active_color: str) -> bool:
    if active_color != 'w' and active_color != 'b':
        raise Exception('active color not valid')
    return True


def validate_fen_castling_rights(castling_rights: str):
    possible_castling_rights = ['Q', 'K', 'k', 'q', '-']
    if len(castling_rights) > 4: raise Exception('too many castling rights chars')
    if len(castling_rights) == 0: raise Exception('castling rights cannot be empty')
    for char in castling_rights:
        if char not in possible_castling_rights:
            raise Exception('castling rights char not valid')
    return True


def validate_fen_en_passant_rights(en_passant_rights: str):
    if len(en_passant_rights) > 2: raise Exception('too mny digits')
    if en_passant_rights != '-': AN.validate_file_and_rank(*en_passant_rights)
    return True


def validate_fen_half_move_clock(half_move_clock: str):
    if not half_move_clock.isnumeric(): raise Exception('half move clock cannot be a letter')
    if int(half_move_clock) < 0: raise Exception('half move clock cannot be negative')
    if int(half_move_clock) > 100: raise Exception('half move clock cannot be over 100')
    return True


def validate_fen_full_move_number(full_move_number: str):
    if not full_move_number.isnumeric(): raise Exception('full move number cannot be a letter')
    if int(full_move_number) < 0: raise Exception('full move number cannot be negative')
    return True


def validate_fen_data(fen_data: FenData) -> bool:
    validate_fen_piece_placement(fen_data.piece_placement)
    validate_fen_active_color(fen_data.active_color)
    validate_fen_castling_rights(fen_data.castling_rights)
    validate_fen_en_passant_rights(fen_data.en_passant_rights)
    validate_fen_half_move_clock(fen_data.half_move_clock)
    validate_fen_full_move_number(fen_data.full_move_number)
    return True


def encode_fen_data(fen_data: FenData) -> str:
    return ' '.join([
        fen_data.piece_placement,
        fen_data.active_color,
        fen_data.castling_rights,
        fen_data.en_passant_rights,
        fen_data.half_move_clock,
        fen_data.full_move_number
    ])


def decode_fen_notation(fen_notation: str) -> FenData:
    data = fen_notation.split()
    if len(data) != 6: raise Exception("number of arguments in fen notation is incorrect")
    fen_data = FenData(*data)
    validate_fen_data(fen_data)
    return fen_data
# -------------
