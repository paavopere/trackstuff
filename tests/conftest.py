"""Shared test fixtures."""
import os
import pytest
from pathlib import Path


@pytest.fixture(autouse=True)
def isolated_state(tmp_path: Path):
    """
    Automatically isolate state file for each test.
    Sets the state file to a temporary location via environment variable.
    """
    state_file = tmp_path / "state.json"
    old_env = os.environ.get("TRACKSTUFF_STATE_PATH")
    os.environ["TRACKSTUFF_STATE_PATH"] = str(state_file)
    yield state_file
    if old_env:
        os.environ["TRACKSTUFF_STATE_PATH"] = old_env
    else:
        del os.environ["TRACKSTUFF_STATE_PATH"]

