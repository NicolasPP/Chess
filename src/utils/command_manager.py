import enum
import pickle


class Type(enum.Enum):
    UPDATE_FEN = enum.auto()
    END_GAME = enum.auto()
    MOVE = enum.auto()
    INVALID_MOVE = enum.auto()
    UPDATE_CAP_PIECES = enum.auto()
    PICKING_PROMOTION = enum.auto()


class Destination(enum.Enum):
    CLIENT = enum.auto()
    SERVER = enum.auto()


class Command:
    @staticmethod
    def is_name_valid(name: str) -> bool:
        try:
            cmd = Type[name]
            return True
        except KeyError:
            return False

    def __init__(self, name: str, **information):
        assert Command.is_name_valid(name)
        self.name = name
        self.info: dict[str, str] = {key: str(value) for key, value in information.items()}


class CommandManager:

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
    def get(cmd_type: Type, **information) -> Command:
        return Command(cmd_type.name, **information)
