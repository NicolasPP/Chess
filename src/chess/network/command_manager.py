import enum
import pickle
import queue


class ClientCommand(enum.Enum):
    # commands that the client can send to the server
    MOVE = enum.auto()
    PICKING_PROMOTION = enum.auto()
    RESIGN = enum.auto()
    OFFER_DRAW = enum.auto()
    DRAW_RESPONSE = enum.auto()
    TIME_OUT = enum.auto()


class ServerCommand(enum.Enum):
    # commands that the server can send to the client
    UPDATE_FEN = enum.auto()
    END_GAME = enum.auto()
    INVALID_MOVE = enum.auto()
    UPDATE_CAP_PIECES = enum.auto()
    INIT_INFO = enum.auto()
    CLIENT_PROMOTING = enum.auto()
    CLIENT_DRAW_OFFER = enum.auto()
    CONTINUE = enum.auto()


class Command:
    @staticmethod
    def is_name_valid(name: str) -> bool:
        return name in [command.name for command in list(ClientCommand) + list(ServerCommand)]

    def __init__(self, name: str, **information):
        assert Command.is_name_valid(name), f"{name} IS NOT A VALID COMMAND NAME"
        self.name = name
        self.info: dict[str, str] = {key: str(value) for key, value in information.items()}


class CommandManager:
    # for local commands
    MATCH: queue.Queue[Command] = queue.Queue()
    PLAYER: queue.Queue[Command] = queue.Queue()

    # command info keys
    fen_notation: str = 'fen_notation'
    white_time_left: str = 'white_time_left'
    black_time_left: str = 'black_time_left'
    from_coordinates: str = 'from_coordinates'
    dest_coordinates: str = 'dest_coordinates'
    side: str = 'side'
    target_fen: str = 'target_fen'
    time_iso: str = 'time_iso'
    time: str = 'time'
    captured_pieces: str = 'captured_pieces'
    draw_offer_result: str = 'draw_offer_result'
    game_result_type: str = 'game_result_type'
    game_result: str = 'game_result'
    from_index: str = 'from_index'
    dest_index: str = 'dest_index'

    @staticmethod
    def serialize_command(command: Command) -> bytes:
        return pickle.dumps(command)

    @staticmethod
    def serialize_command_list(commands: list[Command]) -> bytes:
        return pickle.dumps(commands)

    @staticmethod
    def deserialize_command_bytes(command_bytes: bytes) -> Command:
        return pickle.loads(command_bytes)

    @staticmethod
    def deserialize_command_list_bytes(command_bytes: bytes) -> list[Command]:
        return pickle.loads(command_bytes)

    @staticmethod
    def get(cmd_type: ClientCommand | ServerCommand, information: dict[str, str] | None = None) -> Command:
        if information is None: return Command(cmd_type.name)
        return Command(cmd_type.name, **information)

    @staticmethod
    def send_to(dest: queue.Queue, command: Command) -> None:
        dest.put(command)

    @staticmethod
    def read_from(command_q: queue.Queue) -> Command | None:
        if command_q.empty(): return None
        return command_q.get()
