class EventDispatcher:
    """Minimal event dispatcher for GUI or console interfaces."""

    def __init__(self):
        self._subscribers = {}

    def subscribe(self, event_name: str, callback):
        self._subscribers.setdefault(event_name, []).append(callback)

    def dispatch(self, event_name: str, *args, **kwargs):
        for cb in self._subscribers.get(event_name, []):
            cb(*args, **kwargs)
