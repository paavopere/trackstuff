"""Tests for SimpleTracker."""

from trackstuff.trackers.simple import SimpleTracker


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
        assert data == {"kind": "simple", "name": "test", "entries": ["123", "abc"]}
