from trackstuff.trackers import Tracker

class SimpleTracker(Tracker):
    entries: list

    def __init__(self, name: str, entries: list | None = None):
        self.name = name
        if entries is None:
            entries = []
        self.entries = entries

    def to_dict(self) -> dict:
        return {"kind": "simple", "name": self.name, "entries": self.entries}

    def add_entry(self, entry: str) -> None:
        self.entries.append(entry)

