from __future__ import annotations

import csv
import logging
import json
from pathlib import Path
from pprint import pformat
from typing import Any, Sized, TypeAlias, Type

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure


_log = logging.getLogger(__name__)
STATE_FILE = "state.json"


type StateDict = dict


class State:
    def __init__(self, state_dict: StateDict):
        self._state_dict = state_dict

    @classmethod
    def load(cls):
        try:
            return cls(state_dict=_load_state())
        except FileNotFoundError as e:
            _log.info('creating new state')
            return cls(state_dict=_init_state())

    def save(self):
        _save_state(self._state_dict)

    def get_tracker(self, name: str) -> Tracker:
        trackers = self._state_dict["trackers"]
        for t in trackers:
            if t.name == name:
                return t
        else:
            raise KeyError(f"tracker {name} not found")
        
    def add_tracker(self, tracker: Tracker):
        existing_trackers = self._state_dict["trackers"]
        existing_names = [t.name for t in existing_trackers]
        if tracker.name in existing_names:
            raise ValueError(f"{tracker.name} already exists")
        else:
            self._state_dict["trackers"].append(tracker)
        _log.info(f'added {tracker}')
        


class Tracker:
    name: str
    entries: Sized

    @classmethod
    def from_dict(cls, d: dict):
        kind = d["kind"]
        if kind == "simple":
            return SimpleTracker(name=d["name"], entries=d["entries"])
        elif kind == "csv":
            return CsvTracker(name=d["name"], path=Path(d["path"]))
        else:
            raise KeyError(f"unknown tracker kind {kind}")

    def __len__(self):
        return len(self.entries)

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name!r})"

    def add_entry(self, entry):
        raise NotImplementedError()

    def to_dict(self):
        raise NotImplementedError()


class SimpleTracker(Tracker):
    entries: list

    def __init__(self, name: str, entries: list | None = None):
        self.name = name
        if entries is None:
            entries = []
        self.entries = entries

    def to_dict(self) -> dict:
        return {"kind": "simple", "name": self.name, "entries": self.entries}

    def add_entry(self, entry):
        self.entries.append(entry)


class CsvTracker(Tracker):

    def __init__(self, name: str, path: Path):
        self.name = name
        self.path = path.absolute()

    def to_dict(self):
        return dict(
            kind="csv",
            name=self.name,
            path=str(self.path)
        )

    # TODO implement adding entries to csv
    # def add_entry(self):
    #   ...

    @property
    def columns(self):
        with open(self.path) as f:
            return csv.DictReader(f).fieldnames

    @property
    def entries(self):
        with open(self.path) as f:
            return [r for r in csv.DictReader(f)]

    # TODO make generic for other kinds of trackers
    def create_plot(self, x: str, y: str, path: Path) -> None:
        """
        Create a plot from the CSV data and save it to the specified path.
        """
        df = pd.read_csv(self.path, parse_dates=[x])
        df.set_index(x, inplace=True)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        df[y].plot(ax=ax, marker='o', linestyle='-', markersize=4)
        ax.set_title(f'{self.name}: {y}({x})')
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.set_xlabel(x)
        ax.set_ylabel(y)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        plt.savefig(path)
        plt.close(fig)
    


def _init_state() -> StateDict:
    return {"trackers": []}



def _load_state() -> StateDict:
    with open(STATE_FILE) as f:
        d = json.load(f)
    state = {"trackers": [Tracker.from_dict(t) for t in d["trackers"]]}
    return state



def _save_state(state: StateDict):
    serialized = {"trackers": [t.to_dict() for t in state["trackers"]]}
    with open(STATE_FILE, "w") as f:
        json.dump(serialized, f, indent=2)
        _log.info(f"saved {STATE_FILE}")
