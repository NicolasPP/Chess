import dataclasses
import enum
import re
import typing

from chess.piece_movement import get_available_moves
from utils.forsyth_edwards_notation import Fen, FenChars
from utils.algebraic_notation import AlgebraicNotation, get_an_from_index

TagPairs: typing.TypeAlias = dict[str, str]


class PGNChars(enum.Enum):
    CHECK: str = '+'
    CHECKMATE: str = '#'
    TAKE: str = 'x'
    EN_PASSANT: str = '='


@dataclasses.dataclass
class PGNMove:
    white_move: str
    black_move: str
    white_clock: str
    black_clock: str


@dataclasses.dataclass
class Game:
    pgn_string: str
    tag_pairs: TagPairs
    pgn_moves: list[PGNMove]
    result: str


class PortableGameNotation:
    def __init__(self, file_name: str):
        self.file_name: str = file_name
        self.games: list[Game] = self.parse_pgn_file()

    def parse_pgn_file(self) -> list[Game]:
        games: list[Game] = []
        tag_pairs: TagPairs = {}

        with open(self.file_name, "r") as file:

            lines = file.read().split('\n')

            for line in lines:
                if not line: continue
                if is_tag_pair(line):
                    insert_tag_pair(tag_pairs, line)
                else:
                    games.append(Game(line, tag_pairs, *get_pgn_moves_and_result(line)))
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


def get_an_from_pgn_game(game: Game) \
        -> typing.Generator[tuple[AlgebraicNotation, AlgebraicNotation, str], None, None]:
    fen = Fen()
    for pgn_move in game.pgn_moves:
        if pgn_move.white_move:
            yield process_pgn_move(pgn_move.white_move, fen, True)
        if pgn_move.black_move:
            yield process_pgn_move(pgn_move.black_move, fen, False)


def process_pgn_move(pgn_move: str, fen: Fen, is_white_turn: bool) \
        -> tuple[AlgebraicNotation, AlgebraicNotation, str]:
    from_an, dest_an, target_fen = get_algebraic_notation_from_pgn_move(pgn_move, fen, is_white_turn)
    if not target_fen: target_fen = fen[from_an.data.index]
    fen.make_move(from_an.data.index, dest_an.data.index, target_fen)
    return from_an, dest_an, target_fen


def get_algebraic_notation_from_pgn_move(pgn_move: str, fen: Fen, is_white_turn: bool) \
        -> tuple[AlgebraicNotation, AlgebraicNotation, str]:
    target_fen = ''

    if is_move_castle(pgn_move):
        from_an, dest_an = get_castle_from_dest(pgn_move, is_white_turn)
        return from_an, dest_an, target_fen

    is_check = pgn_move[-1] is PGNChars.CHECK.value
    is_checkmate = pgn_move[-1] is PGNChars.CHECKMATE.value
    is_take = pgn_move.find(PGNChars.TAKE.value) >= 0
    is_en_passant = pgn_move.find(PGNChars.EN_PASSANT.value) >= 0 and not pgn_move[-1].isnumeric()

    if is_check:
        pgn_move = pgn_move.replace(PGNChars.CHECK.value, '')
    if is_take:
        pgn_move = pgn_move.replace(PGNChars.TAKE.value, '')
    if is_checkmate:
        pgn_move = pgn_move.replace(PGNChars.CHECKMATE.value, '')
    if is_en_passant:
        pgn_move = pgn_move.replace(PGNChars.EN_PASSANT.value, '')
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
    king_an = get_an_from_index(king_index)
    if pgn_move == 'O-O-O': return king_an, get_an_from_index(queen_side_rook_index)
    return king_an, get_an_from_index(king_side_rook_index)


def disambiguate_pgn_from_move(dest_an: AlgebraicNotation, pgn_from_info: str, fen: Fen,
                               is_white_turn) -> AlgebraicNotation:
    piece_fen, file_filter, rank_filter = parse_pgn_from_info(pgn_from_info, is_white_turn)
    similar_pieces_indexes = fen.get_indexes_for_piece(piece_fen)
    from_index = -1
    for s_index in similar_pieces_indexes:
        index_an = get_an_from_index(s_index)
        if file_filter and index_an.data.file != file_filter.lower(): continue
        if rank_filter and index_an.data.rank != rank_filter.lower(): continue
        similar_piece_available_moves = get_available_moves(piece_fen, s_index, fen, is_white_turn)
        for move in similar_piece_available_moves:
            if move == dest_an.data.index: from_index = s_index
            if from_index != -1: break
        if from_index != -1: break
    return get_an_from_index(from_index)


def parse_pgn_from_info(pgn_from_info: str, is_white_turn: bool) -> tuple[str, str | None, str | None]:
    pawn_fen = FenChars.DEFAULT_PAWN.get_piece_fen(is_white_turn)
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
