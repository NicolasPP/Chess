from __future__ import annotations

from queue import Queue
from typing import Optional

from event.game_events import GameEvent


class LocalEvents:
    events: Optional[LocalEvents] = None

    @staticmethod
    def get() -> LocalEvents:
        if LocalEvents.events is None:
            LocalEvents.events = LocalEvents()

        return LocalEvents.events

    def __init__(self) -> None:
        self.match: Queue[GameEvent] = Queue()
        self.player: Queue[GameEvent] = Queue()

    def get_match_event(self) -> Optional[GameEvent]:
        if self.match.empty():
            return None

        return self.match.get()

    def get_player_event(self) -> Optional[GameEvent]:
        if self.player.empty():
            return None

        return self.player.get()

    def add_player_event(self, event: GameEvent) -> None:
        self.player.put(event)

    def add_match_event(self, event: GameEvent) -> None:
        self.match.put(event)
