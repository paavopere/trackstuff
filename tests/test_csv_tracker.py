"""Tests for CsvTracker."""
import pytest
from pathlib import Path

from trackstuff.trackers.csv import CsvTracker


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

