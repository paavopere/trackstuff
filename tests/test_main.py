import pytest
import os
from pathlib import Path

from trackstuff.main import State, SimpleTracker, CsvTracker


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


class TestSimpleTracker:
    """Tests for SimpleTracker functionality."""
    
    def test_simple_tracker(self):
        """
        Test that a simple tracker can be created, entries can be added,
        and it can be serialized to a dictionary.
        """
        # Test creation and basic operations
        tracker = SimpleTracker("test")
        assert tracker.name == "test"
        assert len(tracker.entries) == 0
        assert len(tracker) == 0
        
        # Test adding entries
        tracker.add_entry("123")
        tracker.add_entry("abc")
        assert tracker.entries == ["123", "abc"]
        assert len(tracker) == 2
        
        # Test serialization
        data = tracker.to_dict()
        assert data == {
            "kind": "simple",
            "name": "test",
            "entries": ["123", "abc"]
        }


class TestCsvTracker:
    """Tests for CsvTracker functionality."""
    
    @pytest.fixture
    def test_csv(self):
        """Path to test CSV file."""
        return Path(__file__).parent / "data" / "date_number.csv"
    
    def test_csv_tracker(self, test_csv: Path):
        """
        Test that a CSV-backed tracker can be created from an existing CSV file, entries can be read,
        and it can be serialized to a dictionary.
        """
        csv_path = test_csv
        
        # Test creation
        tracker = CsvTracker("test", csv_path)
        assert tracker.name == "test"
        assert tracker.path == csv_path.absolute()
        
        # Test reading entries
        entries = tracker.entries
        assert len(entries) == 100
        assert entries[0]["date"] == "2020-01-01"
        assert entries[0]["number"] == "72.5"
        
        # Test serialization
        data = tracker.to_dict()
        assert data == {
            "kind": "csv",
            "name": "test",
            "path": str(csv_path.absolute())
        }

    def test_csv_tracker_add_entry(self, test_csv: Path, tmp_path: Path):
        """
        Test that entries can be added to a CSV tracker.
        """
        # Copy test file to tmp so we can modify it
        csv_path = tmp_path / "test.csv"
        csv_path.write_text(test_csv.read_text())
        
        # Create tracker and add entry
        tracker = CsvTracker("test", csv_path)
        len_before = len(tracker.entries)
        tracker.add_entry('{"date": "2025-01-01", "number": "100.0"}')
        
        # Verify entry was added
        entries = tracker.entries
        assert len(entries) == len_before + 1
        assert entries[100]["date"] == "2025-01-01"
        assert entries[100]["number"] == "100.0"
        
        # Verify CSV file was updated
        csv_content = csv_path.read_text()
        assert "2025-01-01,100.0" in csv_content

    def test_csv_tracker_add_entry_json_string(self, test_csv: Path, tmp_path: Path):
        """
        Test that a JSON string entry is parsed and added.
        """
        csv_path = tmp_path / "test.csv"
        csv_path.write_text(test_csv.read_text())
        
        tracker = CsvTracker("test", csv_path)
        len_before = len(tracker.entries)
        tracker.add_entry('{"date": "2025-01-01", "number": "100.0"}')
        
        entries = tracker.entries
        assert len(entries) == len_before + 1
        assert entries[100]["date"] == "2025-01-01"
        assert entries[100]["number"] == "100.0"

    @pytest.mark.parametrize("invalid_entry", [
        None,
        "",
        "not-json",
        '["not", "an", "object"]',
        '{"date": "2023-01-02", "number": 2, "nonexistent_column": "value"}',
    ])
    def test_csv_tracker_add_entry_invalid(self, tmp_path: Path, invalid_entry: str):
        """
        Test that invalid entries are rejected.
        """
        test_file = Path(__file__).parent / "data" / "date_number.csv"
        csv_path = tmp_path / "test.csv"
        csv_path.write_text(test_file.read_text())
        
        tracker = CsvTracker("test", csv_path)
        
        with pytest.raises(Exception):
            tracker.add_entry(invalid_entry)

    def test_csv_tracker_add_entry_handles_newlines(self, tmp_path: Path):
        """
        Test that adding an entry produces consistent CSV output (with trailing newlines) whether or not
        there's a trailing newline in the underlying CSV file
        """
        expected_csv = "date,number\n2023-01-01,80.5\n2023-01-02,81.0\n"
        
        # Test 1: CSV without trailing newline
        csv_path_no_newline: Path = tmp_path / "test_no_newline.csv"
        csv_path_no_newline.write_text("date,number\n2023-01-01,80.5")
        
        tracker = CsvTracker("test", csv_path_no_newline)
        tracker.add_entry('{"date": "2023-01-02", "number": "81.0"}')
        
        assert csv_path_no_newline.read_text() == expected_csv
        
        # Test 2: CSV with trailing newline
        csv_path_with_newline: Path = tmp_path / "test_with_newline.csv"
        csv_path_with_newline.write_text("date,number\n2023-01-01,80.5\n")
        
        tracker = CsvTracker("test", csv_path_with_newline)
        tracker.add_entry('{"date": "2023-01-02", "number": "81.0"}')
        
        assert csv_path_with_newline.read_text() == expected_csv

    def test_csv_tracker_add_entry_to_header_only_file(self, tmp_path: Path):
        """
        Test that adding an entry works when CSV has only headers.
        """
        test_file = Path(__file__).parent / "data" / "date_number_header_only.csv"
        csv_path = tmp_path / "test.csv"
        csv_path.write_text(test_file.read_text())
        
        tracker = CsvTracker("test", csv_path)
        tracker.add_entry('{"date": "2023-01-01", "number": "80.5"}')
        
        # Verify entry was added correctly
        entries = tracker.entries
        assert len(entries) == 1
        assert entries[0]["date"] == "2023-01-01"
        assert entries[0]["number"] == "80.5"

    def test_csv_tracker_add_entry_to_empty_file(self, tmp_path: Path):
        """
        Test that adding an entry to an empty CSV file fails gracefully.
        """
        csv_path: Path = tmp_path / "test.csv"
        # Create an empty file
        csv_path.write_text("")
        
        tracker = CsvTracker("test", csv_path)
        
        # This should fail because there are no columns defined
        with pytest.raises((TypeError, StopIteration)):
            tracker.add_entry('{"date": "2023-01-01", "number": "80.5"}')


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


class TestTrackerBaseClass:
    """Tests for Tracker base class."""
    
    def test_tracker_base_class_not_implemented(self):
        """Test that base Tracker class raises NotImplementedError for abstract methods."""
        from trackstuff.main import Tracker
        
        # Create a minimal subclass that doesn't implement the methods
        class IncompleteTracker(Tracker):
            def __init__(self):
                self.name = "incomplete"
                self.entries = []
        
        tracker = IncompleteTracker()
        
        with pytest.raises(NotImplementedError):
            _ = tracker.columns
        
        with pytest.raises(NotImplementedError):
            tracker.add_entry("data")
        
        with pytest.raises(NotImplementedError):
            tracker.to_dict()

    def test_tracker_from_dict_unknown_kind(self):
        """Test that from_dict raises KeyError for unknown tracker kind."""
        from trackstuff.main import Tracker
        
        with pytest.raises(KeyError, match="unknown tracker kind"):
            Tracker.from_dict({"kind": "unknown", "name": "test"})


class TestStateFileLocation:
    """Tests for state file location configuration."""
    
    def test_get_state_file_default_location(self, monkeypatch):
        """Test that _get_state_file returns the default config directory path."""
        from trackstuff.main import _get_state_file
        
        # Clear both env vars to test default
        monkeypatch.delenv("TRACKSTUFF_STATE_PATH", raising=False)
        monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
        
        state_file = _get_state_file()
        assert state_file == Path.home() / ".config" / "trackstuff" / "state.json"
        assert state_file.parent.exists()  # Config dir should be created

    def test_get_state_file_respects_xdg_config_home(self, monkeypatch, tmp_path: Path):
        """Test that _get_state_file respects XDG_CONFIG_HOME environment variable."""
        from trackstuff.main import _get_state_file
        
        # Clear TRACKSTUFF_STATE_PATH and set XDG_CONFIG_HOME
        monkeypatch.delenv("TRACKSTUFF_STATE_PATH", raising=False)
        custom_config = tmp_path / "custom_config"
        monkeypatch.setenv("XDG_CONFIG_HOME", str(custom_config))
        
        state_file = _get_state_file()
        assert state_file == custom_config / "trackstuff" / "state.json"
        assert state_file.parent.exists()  # Config dir should be created

    def test_get_state_file_respects_trackstuff_state_path(self, monkeypatch, tmp_path: Path):
        """Test that _get_state_file respects TRACKSTUFF_STATE_PATH environment variable."""
        from trackstuff.main import _get_state_file
        
        # Set TRACKSTUFF_STATE_PATH
        custom_state = tmp_path / "my_custom_dir" / "my_state.json"
        monkeypatch.setenv("TRACKSTUFF_STATE_PATH", str(custom_state))
        
        state_file = _get_state_file()
        assert state_file == custom_state
        assert state_file.parent.exists()  # Parent dir should be created
