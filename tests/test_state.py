"""Tests for State management."""
import pytest
from pathlib import Path

from trackstuff.state import State, _get_state_file
from trackstuff.trackers.simple import SimpleTracker
from trackstuff.trackers.csv import CsvTracker


class TestState:
    """Tests for State management."""
    
    def test_state_management(self, tmp_path: Path):
        """
        Test that the State class can manage trackers, including adding trackers,
        retrieving them, and handling duplicates.
        """
        # Set up initial state
        state = State({"trackers": []})
        
        # Add trackers
        simple_tracker = SimpleTracker("simple")
        state.add_tracker(simple_tracker)
        
        csv_path = tmp_path / "test.csv"
        csv_path.write_text("time,mass\n2023-01-01,80.5\n")
        csv_tracker = CsvTracker("csv", csv_path)
        state.add_tracker(csv_tracker)
        
        # Test retrieval
        assert state.get_tracker("simple").name == "simple"
        assert state.get_tracker("csv").name == "csv"
        
        # Test duplicate names
        with pytest.raises(ValueError):
            state.add_tracker(SimpleTracker("simple"))
        
        # Test non-existent tracker
        with pytest.raises(KeyError):
            state.get_tracker("nonexistent")


class TestStateFileLocation:
    """Tests for state file location configuration."""
    
    def test_get_state_file_default_location(self, monkeypatch):
        """Test that _get_state_file returns the default config directory path."""
        # Clear both env vars to test default
        monkeypatch.delenv("TRACKSTUFF_STATE_PATH", raising=False)
        monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
        
        state_file = _get_state_file()
        assert state_file == Path.home() / ".config" / "trackstuff" / "state.json"
        assert state_file.parent.exists()  # Config dir should be created

    def test_get_state_file_respects_xdg_config_home(self, monkeypatch, tmp_path: Path):
        """Test that _get_state_file respects XDG_CONFIG_HOME environment variable."""
        # Clear TRACKSTUFF_STATE_PATH and set XDG_CONFIG_HOME
        monkeypatch.delenv("TRACKSTUFF_STATE_PATH", raising=False)
        custom_config = tmp_path / "custom_config"
        monkeypatch.setenv("XDG_CONFIG_HOME", str(custom_config))
        
        state_file = _get_state_file()
        assert state_file == custom_config / "trackstuff" / "state.json"
        assert state_file.parent.exists()  # Config dir should be created

    def test_get_state_file_respects_trackstuff_state_path(self, monkeypatch, tmp_path: Path):
        """Test that _get_state_file respects TRACKSTUFF_STATE_PATH environment variable."""
        # Set TRACKSTUFF_STATE_PATH
        custom_state = tmp_path / "my_custom_dir" / "my_state.json"
        monkeypatch.setenv("TRACKSTUFF_STATE_PATH", str(custom_state))
        
        state_file = _get_state_file()
        assert state_file == custom_state
        assert state_file.parent.exists()  # Parent dir should be created

