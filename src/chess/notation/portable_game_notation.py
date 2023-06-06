import dataclasses
import re
import typing

from chess.movement.piece_movement import get_available_moves
from chess.movement.piece_movement import is_pawn_promotion
from chess.movement.validate_move import is_check
from chess.movement.validate_move import is_checkmate
from chess.movement.validate_move import is_take
from chess.notation.algebraic_notation import AlgebraicNotation
from chess.notation.forsyth_edwards_notation import Fen
from chess.notation.forsyth_edwards_notation import FenChars

TagPairs: typing.TypeAlias = dict[str, str]


class PGNChars:
    CHECK: str = '+'
    CHECKMATE: str = '#'
    TAKE: str = 'x'
    PROMOTION: str = '='
    KING_SIDE_CASTLE: str = 'O-O'
    QUEEN_SIDE_CASTLE: str = 'O-O-O'


@dataclasses.dataclass
class PGNMove:
    white_move: str
    black_move: str
    white_clock: str
    black_clock: str


@dataclasses.dataclass
class PGNGame:
    pgn_string: str
    tag_pairs: TagPairs
    pgn_moves: list[PGNMove]
    result: str


@dataclasses.dataclass
class RegMove:
    from_an: AlgebraicNotation
    dest_an: AlgebraicNotation
    target_fen: str


@dataclasses.dataclass
class RegMovePair:
    white_move: RegMove | None
    black_move: RegMove | None


class PortableGameNotation:
    def __init__(self, file_name: str):
        self.file_name: str = file_name
        self.games: list[PGNGame] = self.parse_pgn_file()

    def parse_pgn_file(self) -> list[PGNGame]:
        games: list[PGNGame] = []
        tag_pairs: TagPairs = {}

        with open(self.file_name, "r") as file:

            lines = file.read().split('\n')

            for line in lines:
                if not line: continue
                if is_tag_pair(line):
                    insert_tag_pair(tag_pairs, line)
                else:
                    games.append(PGNGame(line, tag_pairs, *get_pgn_moves_and_result(line)))
                    tag_pairs = {}

            file.close()

        return games


def is_tag_pair(line: str):
    return line[0] == '[' and line[-1] == ']'


def insert_tag_pair(tag_pairs: TagPairs, line: str) -> None:
    line = line.replace('[', '')
    line = line.replace(']', '')
    name, val = line.split(' ', 1)
    val = val.replace('"', '')
    tag_pairs[name] = val


def get_pgn_moves_and_result(line: str) -> tuple[list[PGNMove], str]:
    split_line = r'[0-9A-Za-z]+\.'
    move_list = re.split(split_line, line)
    pgn_moves: list[PGNMove] = []
    result: str = ''
    for move in move_list:
        if not move: continue

        curly_brackets_content_pattern = r'\{[^}]*\}'
        move_set = re.sub(curly_brackets_content_pattern, '', move).split()
        time_set = re.findall(curly_brackets_content_pattern, move)

        if len(time_set) == 0: time_set = ['', '']
        if len(time_set) == 1: time_set.append('')
        if len(move_set) == 3:
            result = move_set.pop(-1)
        elif is_result(move_set[1]):
            result = move_set[1]
            move_set[1] = ''

        move_set = list(map(lambda m: m.strip(), move_set))
        time_set = list(map(lambda time: time.strip(), time_set))

        pgn_moves.append(PGNMove(*move_set, *time_set))

        assert len(move_set) == 2 or len(move_set) == 3, f'{move}  {line}'
        assert len(time_set) == 2, f'{move}  {time_set}'
    assert result != '', 'result not found'
    return pgn_moves, result


def is_result(move: str) -> bool:
    possible_results = ['1-0', '0-1', '1/2-1/2']
    return move in possible_results


def get_an_from_pgn_game(game: PGNGame) \
        -> typing.Generator[RegMovePair, None, None]:
    fen = Fen()
    for pgn_move in game.pgn_moves:
        white_move = None
        black_move = None
        if pgn_move.white_move:
            white_move = process_pgn_move(pgn_move.white_move, fen, True)
        if pgn_move.black_move:
            black_move = process_pgn_move(pgn_move.black_move, fen, False)

        yield RegMovePair(white_move, black_move)


def process_pgn_move(pgn_move: str, fen: Fen, is_white_turn: bool) \
        -> RegMove:
    from_an, dest_an, target_fen = get_algebraic_notation_from_pgn_move(pgn_move, fen, is_white_turn)
    if not target_fen: target_fen = fen[from_an.index]
    fen.make_move(from_an.index, dest_an.index, target_fen)
    return RegMove(from_an, dest_an, target_fen)


def get_algebraic_notation_from_pgn_move(pgn_move: str, fen: Fen, is_white_turn: bool) \
        -> tuple[AlgebraicNotation, AlgebraicNotation, str]:
    target_fen = ''

    if is_move_castle(pgn_move):
        from_an, dest_an = get_castle_from_dest(pgn_move, is_white_turn)
        return from_an, dest_an, target_fen

    is_move_check = pgn_move[-1] is PGNChars.CHECK
    is_move_checkmate = pgn_move[-1] is PGNChars.CHECKMATE
    is_move_take = pgn_move.find(PGNChars.TAKE) >= 0
    is_promotion = pgn_move.find(PGNChars.PROMOTION) >= 0 and not pgn_move[-1].isnumeric()

    if is_move_check:
        pgn_move = pgn_move.replace(PGNChars.CHECK, '')
    if is_move_take:
        pgn_move = pgn_move.replace(PGNChars.TAKE, '')
    if is_move_checkmate:
        pgn_move = pgn_move.replace(PGNChars.CHECKMATE, '')
    if is_promotion:
        pgn_move = pgn_move.replace(PGNChars.PROMOTION, '')
        target_fen = pgn_move[-1].upper() if is_white_turn else pgn_move[-1].lower()
        pgn_move = pgn_move[:-1]

    # at this point it is safe to extract the destination
    dest_coordinates = pgn_move[-2:]

    # the remaining string(pgn_move) becomes the from_piece information
    pgn_move = pgn_move[:-2]

    dest_an = AlgebraicNotation(*dest_coordinates)

    from_an = disambiguate_pgn_from_move(dest_an, pgn_move, fen, is_white_turn)
    return from_an, dest_an, target_fen


def is_move_castle(pgn_move) -> bool:
    if len(pgn_move) != 3 and len(pgn_move) != 5: return False
    if pgn_move[0] != 'O': return False
    if pgn_move[-1] != 'O': return False
    return True


def get_castle_from_dest(pgn_move, is_white_turn) -> tuple[AlgebraicNotation, AlgebraicNotation]:
    king_side_rook_index = 63 if is_white_turn else 7
    queen_side_rook_index = 56 if is_white_turn else 0
    king_index = 60 if is_white_turn else 4
    king_an = AlgebraicNotation.get_an_from_index(king_index)
    if pgn_move == 'O-O-O': return king_an, AlgebraicNotation.get_an_from_index(queen_side_rook_index)
    return king_an, AlgebraicNotation.get_an_from_index(king_side_rook_index)


def disambiguate_pgn_from_move(dest_an: AlgebraicNotation, pgn_from_info: str, fen: Fen,
                               is_white_turn) -> AlgebraicNotation:
    piece_fen, file_filter, rank_filter = parse_pgn_from_info(pgn_from_info, is_white_turn)
    similar_pieces_indexes = fen.get_indexes_for_piece(piece_fen)
    from_index = -1
    for s_index in similar_pieces_indexes:
        index_an = AlgebraicNotation.get_an_from_index(s_index)
        if file_filter and index_an.file != file_filter.lower(): continue
        if rank_filter and index_an.rank != rank_filter.lower(): continue
        similar_piece_available_moves = get_available_moves(s_index, fen, is_white_turn)
        for move in similar_piece_available_moves:
            if move == dest_an.index: from_index = s_index
            if from_index != -1: break
        if from_index != -1: break
    return AlgebraicNotation.get_an_from_index(from_index)


def parse_pgn_from_info(pgn_from_info: str, is_white_turn: bool) -> tuple[str, str | None, str | None]:
    pawn_fen = FenChars.get_piece_fen(FenChars.DEFAULT_PAWN, is_white_turn)
    if not pgn_from_info: return pawn_fen, None, None

    possible_fen = ['B', 'Q', 'R', 'N', 'K']
    piece_fen = pgn_from_info[0]
    pgn_from_info = pgn_from_info[1:]

    if piece_fen not in possible_fen:
        file_filter, rank_filter = get_file_rank_filter(piece_fen)
        return pawn_fen, file_filter, rank_filter

    piece_fen = piece_fen.upper() if is_white_turn else piece_fen.lower()
    file_filter, rank_filter = get_file_rank_filter(pgn_from_info)

    return piece_fen, file_filter, rank_filter


def get_file_rank_filter(pgn_from_info: str) -> tuple[str | None, str | None]:
    file_filter, rank_filter = None, None

    if not pgn_from_info: return file_filter, rank_filter

    if len(pgn_from_info) == 1:
        if pgn_from_info.isnumeric():
            rank_filter = pgn_from_info
        else:
            file_filter = pgn_from_info
    else:
        file_filter, rank_filter = list(pgn_from_info)

    return file_filter, rank_filter


def generate_move_text(fen: Fen, from_an: AlgebraicNotation, dest_an: AlgebraicNotation, target_fen: str) -> str:
    from_piece_val = fen[from_an.index]
    post_move_fen: Fen = Fen(fen.notation)
    post_move_fen.make_move(from_an.index, dest_an.index, target_fen)
    is_move_check: bool = is_check(post_move_fen)
    is_move_checkmate: bool = is_checkmate(post_move_fen)
    suffix: str = ''

    if is_move_check:
        suffix = PGNChars.CHECK

    if is_move_checkmate:
        suffix = PGNChars.CHECKMATE

    if from_piece_val == FenChars.get_piece_fen(FenChars.DEFAULT_PAWN, fen.is_white_turn()):
        return disambiguate_pawn_move(fen, from_an, dest_an, target_fen) + suffix

    elif from_piece_val == FenChars.get_piece_fen(FenChars.DEFAULT_KING, fen.is_white_turn()):
        return disambiguate_king_move(fen, from_an, dest_an) + suffix

    else:
        return disambiguate_move(fen, from_an, dest_an) + suffix


def disambiguate_pawn_move(fen: Fen, from_an: AlgebraicNotation,
                           dest_an: AlgebraicNotation, target_fen: str) -> str:
    if is_pawn_promotion(from_an, dest_an, fen):
        return dest_an.coordinates + PGNChars.PROMOTION + target_fen.upper()

    is_en_passant = fen.is_move_en_passant(from_an.index, dest_an.index)
    is_move_take = is_take(fen, dest_an.index, is_en_passant, False)
    if is_move_take:
        return from_an.file + PGNChars.TAKE + dest_an.coordinates
    else:
        return dest_an.coordinates


def disambiguate_move(fen: Fen, from_an: AlgebraicNotation,
                      dest_an: AlgebraicNotation) -> str:
    indexes_for_piece: list[int] = fen.get_indexes_for_piece(fen[from_an.index])
    from_val: str = fen[from_an.index]
    is_castle = fen.is_move_castle(from_an.index, dest_an.index)
    is_move_take: bool = is_take(fen, dest_an.index, False, is_castle)
    take_val: str = PGNChars.TAKE if is_move_take else ''
    if len(indexes_for_piece) == 1: return from_val.upper() + take_val + dest_an.coordinates
    file_id: bool = True
    rank_id: bool = True
    disambiguate: bool = False
    for index in indexes_for_piece:
        if index == from_an.index: continue
        for move_index in get_available_moves(index, fen):
            if move_index == dest_an.index:
                disambiguate = True
                an = AlgebraicNotation.get_an_from_index(index)
                if an.file == from_an.file:
                    file_id = False
                elif an.rank == from_an.rank:
                    rank_id = False
    # square
    if not file_id and not rank_id:
        return from_val.upper() + from_an.coordinates + take_val + dest_an.coordinates

    # no need to disambiguate
    elif file_id and rank_id:
        if disambiguate:
            return from_val.upper() + from_an.file + take_val + dest_an.coordinates
        return from_val.upper() + take_val + dest_an.coordinates

    elif file_id:
        return from_val.upper() + from_an.file + take_val + dest_an.coordinates

    else:
        return from_val.upper() + from_an.rank + take_val + dest_an.coordinates


def disambiguate_king_move(fen: Fen, from_an: AlgebraicNotation,
                           dest_an: AlgebraicNotation) -> str:
    if fen.is_move_castle(from_an.index, dest_an.index):
        queen_side_rook_index = 56 if fen.is_white_turn() else 0

        if dest_an.index == queen_side_rook_index:
            return PGNChars.QUEEN_SIDE_CASTLE
        else:
            return PGNChars.KING_SIDE_CASTLE
    else:
        is_move_take = fen[dest_an.index] != FenChars.BLANK_PIECE
        take_val: str = PGNChars.TAKE if is_move_take else ''
        return fen[from_an.index].upper() + take_val + dest_an.coordinates
