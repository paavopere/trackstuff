from __future__ import annotations

import csv
import logging
import json
from pathlib import Path
from typing import Sized

import pandas as pd

from trackstuff.plotting import plot_to_file, plot_to_terminal


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
        except FileNotFoundError:
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

    @property
    def columns(self):
        raise NotImplementedError()

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

    def to_dataframe(self) -> pd.DataFrame:
        """
        Load the CSV data as a pandas DataFrame.
        """
        return pd.read_csv(self.path)

    def create_plot(self, x: str, y: str, path: Path) -> None:
        """
        Create a plot from the CSV data and save it to the specified path.
        """
        df = self.to_dataframe()
        plot_to_file(df, x=x, y=y, path=path, name=self.name)
    
    def plot_terminal(self, x: str, y: str) -> None:
        """
        Plot data in the terminal using plotext.
        """
        df = self.to_dataframe()
        plot_to_terminal(df, x=x, y=y, name=self.name)


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
