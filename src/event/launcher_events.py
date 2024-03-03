from event.event import Event
from event.event import EventContext
from event.event import EventType


class LauncherEvent(Event):
    def __init__(self, event_type: EventType):
        super().__init__(event_type, EventContext.LAUNCHER)


# -- Events sent from the Client to the Server --
class ServerVerificationEvent(LauncherEvent):

    def __init__(self, user_name: str, elo: int, id_: int, password: str) -> None:
        super().__init__(EventType.SERVER_VERIFICATION)
        self.user_name: str = user_name
        self.elo: int = elo
        self.id: int = id_
        self.password: str = password


class EnterQueueEvent(LauncherEvent):

    def __init__(self) -> None:
        super().__init__(EventType.ENTER_QUEUE)


# -- Events sent from the Server to the Client --

class LaunchGameEvent(LauncherEvent):

    def __init__(self, match_id: int, time: float, side: str) -> None:
        super().__init__(EventType.LAUNCH_GAME)
        self.match_id: int = match_id
        self.time: float = time
        self.side: str = side


class DisconnectEvent(LauncherEvent):

    def __init__(self, reason: str) -> None:
        super().__init__(EventType.DISCONNECT)
        self.reason: str = reason
