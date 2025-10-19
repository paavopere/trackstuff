import json
import logging
import os
from pathlib import Path

from trackstuff.trackers import Tracker


_log = logging.getLogger(__name__)


def _get_state_file() -> Path:
    """Get the path to the state file.

    Priority order:
    1. TRACKSTUFF_STATE_PATH environment variable (if set)
    2. XDG_CONFIG_HOME/trackstuff/state.json (if XDG_CONFIG_HOME is set)
    3. ~/.config/trackstuff/state.json (default)
    """
    state_path_override = os.environ.get("TRACKSTUFF_STATE_PATH")
    if state_path_override:
        state_file = Path(state_path_override)
        state_file.parent.mkdir(parents=True, exist_ok=True)
        return state_file

    xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
    config_base = Path(xdg_config_home) if xdg_config_home else Path.home() / ".config"

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
            state_file = _get_state_file()
            with open(state_file) as f:
                d = json.load(f)
            state_dict = {"trackers": [Tracker.from_dict(t) for t in d["trackers"]]}
        except FileNotFoundError:
            _log.info('creating new state')
            state_dict = {"trackers": []}
        return cls(state_dict=state_dict)

    def save(self):
        state_file = _get_state_file()
        serialized = {"trackers": [t.to_dict() for t in self._state_dict["trackers"]]}
        with open(state_file, "w") as f:
            json.dump(serialized, f, indent=2)
            _log.info(f"saved {state_file}")

    def get_tracker(self, name: str):
        trackers = self._state_dict["trackers"]
        for t in trackers:
            if t.name == name:
                return t
        raise KeyError(f"tracker {name} not found")

    def add_tracker(self, tracker):
        existing_trackers = self._state_dict["trackers"]
        existing_names = [t.name for t in existing_trackers]
        if tracker.name in existing_names:
            raise ValueError(f"{tracker.name} already exists")
        self._state_dict["trackers"].append(tracker)
        _log.info(f'added {tracker}')
