import dataclasses
import typing

from chess.notation.algebraic_notation import AlgebraicNotation, validate_file_and_rank
from config import *


class FenChars:
    BLANK_PIECE: str = "@"
    SPLIT: str = '/'
    WHITE_ACTIVE_COLOR: str = 'w'
    BLACK_ACTIVE_COLOR: str = 'b'
    EMPTY_INFO: str = '-'
    DEFAULT_PAWN = "P"
    DEFAULT_KING = "K"
    DEFAULT_QUEEN = "Q"
    DEFAULT_BISHOP = "B"
    DEFAULT_ROOK = "R"
    DEFAULT_KNIGHT = "N"

    @staticmethod
    def get_piece_fen(char: str, is_white_turn: bool) -> str:
        possible_values: list[str] = [
            FenChars.DEFAULT_PAWN,
            FenChars.DEFAULT_KING,
            FenChars.DEFAULT_QUEEN,
            FenChars.DEFAULT_BISHOP,
            FenChars.DEFAULT_ROOK,
            FenChars.DEFAULT_KNIGHT
        ]
        if char not in possible_values: raise Exception("char not a piece value")
        if is_white_turn: return char.upper()
        return char.lower()


@dataclasses.dataclass
class FenData:
    piece_placement: str
    active_color: str
    castling_rights: str
    en_passant_rights: str
    half_move_clock: str
    full_move_number: str


class InsufficientMaterialInfo(typing.NamedTuple):
    minor_pieces: list[str]
    is_pawn_present: tuple[bool, bool]
    total_count: int


class Fen:
    def __init__(self, fen_notation: str = GAME_START_FEN):
        self._notation: str = fen_notation
        self.data: FenData = decode_fen_notation(fen_notation)
        self.expanded: list[str] = self.get_expanded()
        self.first_move = False

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
        self.data = decode_fen_notation(new_notation)
        self.expanded = self.get_expanded()

    @notation.deleter
    def notation(self) -> None:
        del self._notation

    def is_white_turn(self) -> bool:
        return self.data.active_color == FenChars.WHITE_ACTIVE_COLOR

    def get_next_active_color(self) -> str:
        if self.is_white_turn():
            return FenChars.BLACK_ACTIVE_COLOR
        else:
            return FenChars.WHITE_ACTIVE_COLOR

    def get_castling_rights(self, from_piece_val: str, from_index: int) -> str:
        if self.data.castling_rights == FenChars.EMPTY_INFO: return self.data.castling_rights
        castling_rights = self.data.castling_rights
        is_white_turn = self.is_white_turn()
        king_side_rook_index = 63 if is_white_turn else 7
        queen_side_rook_index = 56 if is_white_turn else 0
        king_index = 60 if is_white_turn else 4
        king_fen = FenChars.get_piece_fen(FenChars.DEFAULT_KING, is_white_turn)
        queen_fen = FenChars.get_piece_fen(FenChars.DEFAULT_QUEEN, is_white_turn)
        rook_fen = FenChars.get_piece_fen(FenChars.DEFAULT_ROOK, is_white_turn)
        if from_piece_val == rook_fen:
            if from_index == king_side_rook_index:
                castling_rights = castling_rights.replace(king_fen, '')
            elif from_index == queen_side_rook_index:
                castling_rights = castling_rights.replace(queen_fen, '')

        elif from_piece_val == king_fen and from_index == king_index:
            castling_rights = castling_rights.replace(king_fen, '')
            castling_rights = castling_rights.replace(queen_fen, '')

        if len(castling_rights) == 0: return FenChars.EMPTY_INFO
        validate_fen_castling_rights(castling_rights)
        return castling_rights

    def get_en_passant_rights(self, from_piece_val: str, from_index: int, dest_index: int) -> str:
        pawn_fen = FenChars.get_piece_fen(FenChars.DEFAULT_PAWN, self.is_white_turn())
        double_moves_start = list(range(48, 56)) if self.is_white_turn() else list(range(8, 16))
        double_moves_end = list(range(32, 40)) if self.is_white_turn() else list(range(24, 32))

        if from_piece_val != pawn_fen: return FenChars.EMPTY_INFO
        if from_index not in double_moves_start: return FenChars.EMPTY_INFO
        if dest_index not in double_moves_end: return FenChars.EMPTY_INFO

        index_offset = BOARD_SIZE if self.is_white_turn() else BOARD_SIZE * -1
        en_passant_rights = AlgebraicNotation.get_an_from_index(dest_index + index_offset).coordinates
        validate_fen_en_passant_rights(en_passant_rights)

        return en_passant_rights

    def get_half_move_clock(self, from_piece_val: str, dest_piece_val: str) -> str:
        pawn_fen = FenChars.get_piece_fen(FenChars.DEFAULT_PAWN, self.is_white_turn())
        if from_piece_val == pawn_fen or dest_piece_val != FenChars.BLANK_PIECE: return '0'
        half_move_clock = str(int(self.data.half_move_clock) + 1)
        validate_fen_half_move_clock(half_move_clock)
        return half_move_clock

    def get_full_move_number(self) -> str:
        if not self.first_move: return self.data.full_move_number
        full_move_number = str(int(self.data.full_move_number) + 1)
        validate_fen_full_move_number(full_move_number)
        return full_move_number

    def get_expanded(self) -> list[str]:
        expanded_fen: str = ''
        for piece_fen in iterate(self.data.piece_placement):
            if piece_fen.isnumeric():
                expanded_fen += (int(piece_fen) * FenChars.BLANK_PIECE)
            else:
                expanded_fen += piece_fen

        return list(expanded_fen)

    def get_pieces_count(self) -> dict[str, int]:
        pieces_count: dict[str, int] = {}
        for piece_fen in iterate(self.data.piece_placement):
            if piece_fen == FenChars.BLANK_PIECE: continue
            if piece_fen.isnumeric(): continue
            if piece_fen in pieces_count:
                pieces_count[piece_fen] += 1
            else:
                pieces_count[piece_fen] = 1
        return pieces_count

    def get_insufficient_material_info(self) -> InsufficientMaterialInfo:
        pieces_count: dict[str, int] = self.get_pieces_count()
        possible_minor_pieces: list[str] = [
            FenChars.get_piece_fen(FenChars.DEFAULT_KNIGHT, True),
            FenChars.get_piece_fen(FenChars.DEFAULT_KNIGHT, False),
            FenChars.get_piece_fen(FenChars.DEFAULT_BISHOP, True),
            FenChars.get_piece_fen(FenChars.DEFAULT_BISHOP, False),
        ]

        total_count: int = sum(value for key, value in pieces_count.items())
        white_pawn_present: bool = True
        black_pawn_present: bool = True

        if pieces_count.get(FenChars.get_piece_fen(FenChars.DEFAULT_PAWN, True)) is None:
            white_pawn_present = False

        if pieces_count.get(FenChars.get_piece_fen(FenChars.DEFAULT_PAWN, False)) is None:
            black_pawn_present = False

        return InsufficientMaterialInfo(
            list(filter(lambda key: key in possible_minor_pieces, self.expanded)),
            (white_pawn_present, black_pawn_present),
            total_count
        )

    def get_indexes_for_piece(self, piece_fen_val: str) -> list[int]:
        validate_fen_val(piece_fen_val)
        result = []
        for index, fen_val in enumerate(self.expanded):
            if fen_val == piece_fen_val: result.append(index)
        return result

    def get_packed(self) -> str:
        blank_count = 0
        fen_notation, fen_row = [], ''
        for index, fen_val in enumerate(self.expanded):
            if fen_val == FenChars.BLANK_PIECE:
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

    def make_move(self, from_index: int, dest_index: int, target_fen: str, update_data: bool = True) -> None:
        from_piece_val = self[from_index]
        dest_piece_val = self[dest_index]

        if self.is_move_en_passant(from_index, dest_index):
            self.make_en_passant_move(from_index, dest_index)
        elif self.is_move_castle(from_index, dest_index):
            self.make_castle_move(from_index, dest_index)
        else:
            self.make_regular_move(from_index, dest_index, target_fen)

        if update_data:
            self.update_fen_data(from_index, dest_index, from_piece_val, dest_piece_val)

        if not self.first_move: self.first_move = True

    def make_en_passant_move(self, from_index: int, dest_index: int) -> None:
        self.make_regular_move(from_index, dest_index, self[from_index])
        opp_index = AlgebraicNotation(
            AlgebraicNotation.get_an_from_index(dest_index).file,
            AlgebraicNotation.get_an_from_index(from_index).rank
        )
        self[opp_index.index] = FenChars.BLANK_PIECE

    def make_castle_move(self, from_index: int, dest_index: int) -> None:
        king_side_rook_index = 63 if self.is_white_turn() else 7
        queen_side_rook_index = 56 if self.is_white_turn() else 0

        ks_king_index = 62 if self.is_white_turn() else 6
        ks_rook_index = 61 if self.is_white_turn() else 5
        qs_king_index = 58 if self.is_white_turn() else 2
        qs_rook_index = 59 if self.is_white_turn() else 3

        if dest_index == king_side_rook_index:
            self.make_regular_move(from_index, ks_king_index, self[from_index])
            self.make_regular_move(dest_index, ks_rook_index, self[dest_index])
        if dest_index == queen_side_rook_index:
            self.make_regular_move(from_index, qs_king_index, self[from_index])
            self.make_regular_move(dest_index, qs_rook_index, self[dest_index])

    def make_regular_move(self, from_index: int, dest_index: int, target_fen: str) -> None:
        self[dest_index] = target_fen
        self[from_index] = FenChars.BLANK_PIECE

    def is_move_en_passant(self, from_index: int, dest_index: int) -> bool:
        pawn_fen = FenChars.get_piece_fen(FenChars.DEFAULT_PAWN, self.is_white_turn())
        if self.data.en_passant_rights == '-': return False
        if self[from_index] != pawn_fen: return False
        from_an = AlgebraicNotation.get_an_from_index(from_index)
        dest_an = AlgebraicNotation.get_an_from_index(dest_index)
        return from_an.file != dest_an.file and self[dest_index] == FenChars.BLANK_PIECE

    def is_move_castle(self, from_index: int, dest_index: int) -> bool:
        king_fen = FenChars.get_piece_fen(FenChars.DEFAULT_KING, self.is_white_turn())
        rook_fen = FenChars.get_piece_fen(FenChars.DEFAULT_ROOK, self.is_white_turn())
        if self.data.castling_rights == FenChars.EMPTY_INFO: return False
        if self[from_index] != king_fen: return False
        if self[dest_index] != rook_fen: return False
        return True

    def update_fen_data(self, from_index: int, dest_index: int, from_piece_val: str, dest_piece_val: str) -> None:
        self.data.piece_placement = self.get_packed()
        self.data.castling_rights = self.get_castling_rights(from_piece_val, from_index)
        self.data.en_passant_rights = self.get_en_passant_rights(from_piece_val, from_index, dest_index)
        self.data.half_move_clock = self.get_half_move_clock(from_piece_val, dest_piece_val)
        self.data.full_move_number = self.get_full_move_number()
        self.data.active_color = self.get_next_active_color()


def iterate(piece_placement: str) -> typing.Generator[str, None, None]:
    for fen_row in piece_placement.split(FenChars.SPLIT):
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


def validate_fen_val(fen_val: str, expanded_values: bool = False) -> bool:
    possible_values = ['p', 'P', 'b', 'B', 'k', 'K', 'n', 'N', 'q', 'Q', 'r', 'R']
    if expanded_values: possible_values.append(FenChars.BLANK_PIECE)
    if fen_val not in possible_values:
        raise Exception('INVALID fen notation: invalid fen val')
    return True


def validate_fen_active_color(active_color: str) -> bool:
    if active_color != FenChars.BLACK_ACTIVE_COLOR and active_color != FenChars.WHITE_ACTIVE_COLOR:
        raise Exception('active color not valid')
    return True


def validate_fen_castling_rights(castling_rights: str) -> bool:
    possible_castling_rights = ['Q', 'K', 'k', 'q', '-']
    if len(castling_rights) > 4: raise Exception('too many castling rights chars')
    if len(castling_rights) == 0: raise Exception('castling rights cannot be empty')
    for char in castling_rights:
        if char not in possible_castling_rights:
            raise Exception('castling rights char not valid')
    return True


def validate_fen_en_passant_rights(en_passant_rights: str) -> bool:
    if len(en_passant_rights) > 2: raise Exception('too many digits')
    if en_passant_rights != FenChars.EMPTY_INFO: validate_file_and_rank(*en_passant_rights)
    return True


def validate_fen_half_move_clock(half_move_clock: str) -> bool:
    if not half_move_clock.isnumeric(): raise Exception('half move clock cannot be a letter')
    if int(half_move_clock) < 0: raise Exception('half move clock cannot be negative')
    if int(half_move_clock) > 100: raise Exception('half move clock cannot be over 100')
    return True


def validate_fen_full_move_number(full_move_number: str) -> bool:
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
