from __future__ import annotations

import csv
import logging
import json
import os
from pathlib import Path
from typing import Sized

import pandas as pd

from trackstuff.plotting import plot_to_file, plot_to_terminal


_log = logging.getLogger(__name__)


def _get_state_file() -> Path:
    """Get the path to the state file.
    
    Priority order:
    1. TRACKSTUFF_STATE_PATH environment variable (if set)
    2. XDG_CONFIG_HOME/trackstuff/state.json (if XDG_CONFIG_HOME is set)
    3. ~/.config/trackstuff/state.json (default)
    """
    # Allow explicit override via environment variable
    state_path_override = os.environ.get("TRACKSTUFF_STATE_PATH")
    if state_path_override:
        state_file = Path(state_path_override)
        state_file.parent.mkdir(parents=True, exist_ok=True)
        return state_file
    
    # Respect XDG Base Directory specification
    xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config_home:
        config_base = Path(xdg_config_home)
    else:
        config_base = Path.home() / ".config"
    
    config_dir = config_base / "trackstuff"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "state.json"


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

    def add_entry(self, entry: str) -> None:
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

    def add_entry(self, entry: str) -> None:
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

    def add_entry(self, entry: str) -> None:
        entry_dict = json.loads(entry)        
        if not isinstance(entry_dict, dict):
            raise TypeError("Entry must be a JSON that parses to a dict")
        
        columns = self.columns
        if set(entry_dict.keys()) != set(columns):
            raise ValueError(f"Entry keys {set(entry_dict.keys())} do not match CSV columns {set(columns)}")
        
        # Ensure file ends with newline before appending
        with open(self.path, 'r+') as f:
            f.seek(0, 2)  # Go to end of file
            f.seek(f.tell() - 1)  # Go to last character
            last_char = f.read(1)
            if last_char != '\n':
                f.write('\n')
        
        with open(self.path, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writerow(entry_dict)

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
    state_file = _get_state_file()
    with open(state_file) as f:
        d = json.load(f)
    state = {"trackers": [Tracker.from_dict(t) for t in d["trackers"]]}
    return state



def _save_state(state: StateDict):
    state_file = _get_state_file()
    serialized = {"trackers": [t.to_dict() for t in state["trackers"]]}
    with open(state_file, "w") as f:
        json.dump(serialized, f, indent=2)
        _log.info(f"saved {state_file}")
