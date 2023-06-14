import typing

from network.commands.client_commands import ClientLauncherCommand, ClientGameCommand
from network.commands.server_commands import ServerLauncherCommand, ServerGameCommand

command_types: typing.TypeAlias = ClientGameCommand | ClientLauncherCommand | ServerGameCommand | ServerLauncherCommand


class Command:

    @staticmethod
    def is_name_valid(name: str) -> bool:
        commands: list[command_types] = list(ClientGameCommand) + \
                                        list(ClientLauncherCommand) + \
                                        list(ServerGameCommand) + \
                                        list(ServerLauncherCommand)
        return name in [command.name for command in commands]

    def __init__(self, name: str, **information):
        assert Command.is_name_valid(name), f"{name} IS NOT A VALID COMMAND NAME"
        self.name = name
        self.info: dict[str, str] = {key: str(value) for key, value in information.items()}
