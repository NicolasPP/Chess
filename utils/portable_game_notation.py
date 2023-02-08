import typing
import dataclasses
import re

TagPairs: typing.TypeAlias = dict[str, str]


@dataclasses.dataclass
class PGNMove:
    white_move: str
    black_move: str
    white_clock: str
    black_clock: str


@dataclasses.dataclass
class Game:
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
                    games.append(Game(tag_pairs, *get_pgn_moves_and_result(line)))
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
    split_line = '[0-9A-Za-z]+\.'
    move_list = re.split(split_line, line)
    pgn_moves: list[PGNMove] = []
    result: str = ''
    for move in move_list:
        if not move: continue

        curly_brackets_content_pattern = '\{[^}]*\}'
        move_set = re.sub(curly_brackets_content_pattern, '', move).split()
        time_set = re.findall(curly_brackets_content_pattern, move)

        if len(time_set) == 0: time_set = ['', '']
        if len(time_set) == 1: time_set.append('')
        if len(move_set) == 3:
            result = move_set.pop(-1)
        elif is_result(move_set[0]):
            result = move_set[0]
            move_set[0] = ''
        elif is_result(move_set[1]):
            result = move_set[1]
            move_set[1] = ''

        pgn_moves.append(PGNMove(*move_set, *time_set))

        assert len(move_set) == 2 or len(move_set) == 3, f'{move}  {line}'
        assert len(time_set) == 2, f'{move}  {time_set}'
    assert result != '', 'result not found'
    return pgn_moves, result


def is_result(move: str) -> bool:
    possible_results = ['1-0', '0-1', '1/2-1/2']
    return move in possible_results
