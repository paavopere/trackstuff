from __future__ import annotations

from collections.abc import Sized
from pathlib import Path


class Tracker:
    name: str
    entries: Sized

    @classmethod
    def from_dict(cls, d: dict):
        from trackstuff.trackers.csv import CsvTracker
        from trackstuff.trackers.simple import SimpleTracker

        kind = d["kind"]
        if kind == "simple":
            return SimpleTracker(name=d["name"], entries=d["entries"])
        if kind == "csv":
            return CsvTracker(name=d["name"], path=Path(d["path"]))
        raise KeyError(f"unknown tracker kind {kind}")

    def __len__(self):
        return len(self.entries)

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name!r})"

    @property
    def columns(self):
        raise NotImplementedError()

    def add_entry(self, entry: str) -> None:
        raise NotImplementedError()

    def to_dict(self):
        raise NotImplementedError()


__all__ = ["Tracker"]
