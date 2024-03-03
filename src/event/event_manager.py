import pickle
import socket

from event.event import Event


class EventManager:

    @staticmethod
    def dispatch(connection: socket.socket, payload: Event | list[Event]):
        connection.send(pickle.dumps(payload))

    @staticmethod
    def load_events(events_bytes: bytes) -> list[Event]:
        return pickle.loads(events_bytes)

    @staticmethod
    def load_event(events_bytes: bytes) -> Event:
        return pickle.loads(events_bytes)
