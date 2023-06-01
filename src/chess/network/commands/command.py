from chess.network.commands.client_commands import ClientCommand
from chess.network.commands.server_commands import ServerCommand


class Command:
    @staticmethod
    def is_name_valid(name: str) -> bool:
        return name in [command.name for command in list(ClientCommand) + list(ServerCommand)]

    def __init__(self, name: str, **information):
        assert Command.is_name_valid(name), f"{name} IS NOT A VALID COMMAND NAME"
        self.name = name
        self.info: dict[str, str] = {key: str(value) for key, value in information.items()}
