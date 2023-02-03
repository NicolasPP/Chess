import enum
import string
import typing
import dataclasses

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
    halfmove_clock: str
    fullmove_number: str


class Fen:
    def __init__(self, fen_notation: str = GAME_START_FEN, move_history: list[list[int]] | None = None):
        self.notation = fen_notation
        self.data = decode_fen_notation(fen_notation)
        self.expanded: list[str] = self.get_expanded()
        self.move_history: list[list[int]] = move_history if move_history else [[] for _ in self.expanded]

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

    def update(self) -> None:
        self.data.piece_placement = self.get_packed()
        self.notation = encode_fen_data(self.data)

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
        return '/'.join(fen_notation)

    def make_move(self, from_index: int, dest_index: int) -> None:
        self[dest_index] = self[from_index]
        self[from_index] = FenChars.BLANK_PIECE.value

        self.move_history[dest_index] = self.move_history[from_index]
        self.move_history[from_index] = []

        self.move_history[dest_index].append(from_index)

        self.update()


# -- Helpers --
def get_index_from_anc(algebraic_notation_coordinates: str) -> int:
    col_num = algebraic_notation_coordinates[0]
    row_str = algebraic_notation_coordinates[1]
    validate_anc(algebraic_notation_coordinates)
    ascii_str = string.ascii_lowercase
    return ((BOARD_SIZE - int(col_num)) * BOARD_SIZE) + ascii_str.index(row_str)


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


def validate_anc(anc: str) -> bool:
    col_num = anc[0]
    row_str = anc[1]
    if not col_num.isnumeric(): raise IndexError("col should be number")
    if row_str.isnumeric(): raise IndexError("row should be letter")
    if int(col_num) > BOARD_SIZE or row_str > 'h': raise IndexError("invalid index")
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
    if en_passant_rights != '-': validate_anc(en_passant_rights)
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


def encode_fen_data(fen_data: FenData) -> str:
    return ' '.join([
        fen_data.piece_placement,
        fen_data.active_color,
        fen_data.castling_rights,
        fen_data.en_passant_rights,
        fen_data.halfmove_clock,
        fen_data.fullmove_number
    ])


def validate_fen_data(fen_data: FenData) -> bool:
    validate_fen_piece_placement(fen_data.piece_placement)
    validate_fen_active_color(fen_data.active_color)
    validate_fen_castling_rights(fen_data.castling_rights)
    validate_fen_en_passant_rights(fen_data.en_passant_rights)
    validate_fen_half_move_clock(fen_data.halfmove_clock)
    validate_fen_full_move_number(fen_data.fullmove_number)
    return True


def decode_fen_notation(fen_notation: str) -> FenData:
    data = fen_notation.split()
    if len(data) != 6: raise Exception("number of arguments in fen notation is incorrect")
    fen_data = FenData(*data)
    validate_fen_data(fen_data)
    return fen_data
# -------------
