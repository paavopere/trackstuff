import pytest
from pathlib import Path
from textwrap import dedent

from trackstuff.main import State, SimpleTracker, CsvTracker

def test_simple_tracker():
    """
    Test that a simple tracker can be created, entries can be added,
    and it can be serialized to a dictionary.
    """
    # Test creation and basic operations
    tracker = SimpleTracker("test")
    assert tracker.name == "test"
    assert len(tracker.entries) == 0
    
    # Test adding entries
    tracker.add_entry("123")
    tracker.add_entry("abc")
    assert tracker.entries == ["123", "abc"]
    
    # Test serialization
    data = tracker.to_dict()
    assert data == {
        "kind": "simple",
        "name": "test",
        "entries": ["123", "abc"]
    }

def test_csv_tracker(tmp_path: Path):
    """
    Test that a CSV-backed tracker can be created from an existing CSV file, entries can be read,
    and it can be serialized to a dictionary.
    """
    # Create a test CSV file
    csv_path: Path = tmp_path / "test.csv"
    csv_path.write_text(dedent("""
        time,mass
        2023-01-01,80.5
        2023-01-02,81.0
    """).strip())
    
    # Test creation
    tracker = CsvTracker("test", csv_path)
    assert tracker.name == "test"
    assert tracker.path == csv_path.absolute()
    
    # Test reading entries
    entries = tracker.entries
    assert len(entries) == 2
    assert entries[0]["time"] == "2023-01-01"
    assert entries[0]["mass"] == "80.5"
    
    # Test serialization
    data = tracker.to_dict()
    assert data == {
        "kind": "csv",
        "name": "test",
        "path": str(csv_path.absolute())
    }

def test_state_management(tmp_path: Path):
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
