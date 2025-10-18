"""Tests for Tracker base class."""
import pytest

from trackstuff.trackers import Tracker


class TestTrackerBaseClass:
    """Tests for Tracker base class."""
    
    def test_tracker_base_class_not_implemented(self):
        """Test that base Tracker class raises NotImplementedError for abstract methods."""
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
        with pytest.raises(KeyError, match="unknown tracker kind"):
            Tracker.from_dict({"kind": "unknown", "name": "test"})

