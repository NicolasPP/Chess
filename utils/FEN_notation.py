import enum
import string
import typing

from config import *


class FenChars(enum.Enum):
    BLANK_PIECE: str = "@"
    SPLIT: str = '/'


class Fen:
    def __init__(self, fen_notation=GAME_START_FEN):
        validate_fen_notation(fen_notation)
        self.notation: str = fen_notation
        self.expanded: list[str] = self.get_expanded()

    def __getitem__(self, index: int) -> str:
        if index < 0: raise IndexError("no negative index")
        return self.expanded[index]

    def __repr__(self):
        result = ''
        for index, fen_val in enumerate(self.expanded):
            if index % BOARD_SIZE == 0 and index != 0: result += '\n'
            result += fen_val
        return result

    def update_notation(self) -> None:
        self.notation = self.get_packed()

    def get_notation(self) -> str:
        return self.notation

    def get_expanded(self) -> list[str]:
        expanded_fen: str = ''
        for piece_fen in iterate(self.notation):
            if piece_fen.isnumeric():
                expanded_fen += (int(piece_fen) * FenChars.BLANK_PIECE.value)
            elif piece_fen == FenChars.SPLIT.value:
                continue
            else:
                expanded_fen += piece_fen

        return list(expanded_fen)

    def get_packed(self) -> str:
        fen_notation, blank_count = set_blank_fen('')
        for index in range(len(self.expanded)):
            if index % BOARD_SIZE == 0 and index > 0:
                fen_notation, blank_count = set_blank_fen(fen_notation, blank_count)
                fen_notation += FenChars.SPLIT.value
            if self.expanded[index] == FenChars.BLANK_PIECE.value:
                blank_count += 1
            else:
                fen_notation, blank_count = set_blank_fen(fen_notation, blank_count)
                fen_notation += self.expanded[index]

            fen_notation, blank_count = set_blank_fen(fen_notation, blank_count)
        return fen_notation

    def make_move(self, from_index: int, dest_index: int) -> None:
        self.expanded[dest_index] = self.expanded[from_index]
        self.expanded[from_index] = FenChars.BLANK_PIECE.value
        self.update_notation()


# -- Helpers --
def get_index_from_anc(algebraic_notation_coordinates: str) -> int:
    col_num = algebraic_notation_coordinates[0]
    row_str = algebraic_notation_coordinates[1]
    if not col_num.isnumeric(): raise IndexError("col should be number")
    if row_str.isnumeric(): raise IndexError("row should be letter")
    if int(col_num) > BOARD_SIZE or row_str > 'h': raise IndexError("invalid index")
    ascii_str = string.ascii_lowercase
    return ((BOARD_SIZE - int(col_num)) * BOARD_SIZE) + ascii_str.index(row_str)


def iterate(fen_notation: str) -> typing.Generator[str, None, None]:
    for fen_row in fen_notation.split(FenChars.SPLIT.value):
        for piece_fen in fen_row: yield piece_fen


def set_blank_fen(fen_notation: str, blank_count: int = 0) -> tuple[str, int]:
    if blank_count > 0:
        fen_notation += str(blank_count)
        blank_count = 0
    return fen_notation, blank_count


def validate_fen_notation(notation) -> bool:
    count = 0
    possible_vals = ['p', 'P', 'b', 'B', 'k', 'K', 'n', 'N', 'q', 'Q', 'r', 'R']
    for piece_fen in iterate(notation):
        if piece_fen.isnumeric():
            int_fen = int(piece_fen)
            if int_fen == 0: raise Exception('INVALID fen notation: number too small')
            if int_fen > 8: raise Exception('INVALID fen notation: number too big')
            count += int_fen
        else:
            if piece_fen not in possible_vals: raise Exception('INVALID fen notation: invalid fen val')
            count += 1
    assert count == 64, "INVALID fen notation: too many or too few"
    return True
# -------------
