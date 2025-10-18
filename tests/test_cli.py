from pathlib import Path
from unittest.mock import patch
import os

import matplotlib
import pytest
from click.testing import CliRunner

from trackstuff.cli import cli

@pytest.fixture
def non_interactive_backend():
    """Fixture to temporarily switch matplotlib to non-interactive backend."""
    old_backend = matplotlib.get_backend()
    matplotlib.use('Agg')
    yield
    matplotlib.use(old_backend)

@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()

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

@pytest.fixture
def clean_state(tmp_path: Path) -> Path:
    """
    Fixture to create a clean state file for tests.
    """
    state_file = tmp_path / "state.json"
    state_file.write_text('{"trackers": []}')
    return state_file

@pytest.fixture
def test_csv() -> Path:
    """
    Fixture that returns the path to the test CSV file.
    """
    return Path(__file__).parent / "data" / "date_number.csv"


class TestCLI:
    """Tests for CLI functionality."""
    
    def test_debug_flag(self, runner: CliRunner):
        """Test that --debug flag enables debug logging."""
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["--debug", "list"])
            assert result.exit_code == 0


class TestTrackerCreation:
    """Tests for creating and managing trackers."""
    
    def test_create_simple_tracker(self, runner: CliRunner, clean_state: Path):
        """
        Test creating a simple tracker, adding some entries and showing them.
        """
        with runner.isolated_filesystem():
            # Create a simple tracker
            result = runner.invoke(cli, ["create", "simple", "test"])
            assert result.exit_code == 0
            
            # Add some data
            result = runner.invoke(cli, ["track", "test", "123"])
            assert result.exit_code == 0
            result = runner.invoke(cli, ["track", "test", "abc"])
            assert result.exit_code == 0
            
            # Show the data
            result = runner.invoke(cli, ["show", "test"])
            assert result.exit_code == 0
            assert "['123', 'abc']" in result.output

    def test_create_csv_tracker(self, runner: CliRunner, test_csv: Path):
        """
        Test creating a CSV-backed tracker and showing its data.
        """
        with runner.isolated_filesystem():
            # Create a tracker out of the CSV file
            result = runner.invoke(cli, ["create", "csv", "test", "-p", str(test_csv)])
            assert result.exit_code == 0
            
            # Show the data
            result = runner.invoke(cli, ["show", "test"])
            assert result.exit_code == 0
            assert "2020-01-01" in result.output
            assert "72.5" in result.output

    def test_list_trackers(self, runner: CliRunner):
        """
        Test creating multiple trackers and listing them.
        """
        with runner.isolated_filesystem():
            # Create some trackers
            result = runner.invoke(cli, ["create", "simple", "test1"])
            assert result.exit_code == 0
            result = runner.invoke(cli, ["create", "simple", "test2"])
            assert result.exit_code == 0
            
            # List trackers
            result = runner.invoke(cli, ["list"])
            assert result.exit_code == 0
            assert "test1" in result.output
            assert "test2" in result.output
    
    def test_create_csv_tracker_nonexistent_file(self, runner: CliRunner):
        """
        Test that creating a CSV tracker with a non-existent file fails.
        """
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["create", "csv", "test", "-p", "nonexistent.csv"])
            assert result.exit_code == 1
            assert "does not exist" in result.output
    
    def test_create_csv_tracker_duplicate_name(self, runner: CliRunner, test_csv: Path):
        """
        Test that creating a CSV tracker with a duplicate name fails.
        """
        with runner.isolated_filesystem():
            # Create first tracker
            result = runner.invoke(cli, ["create", "csv", "test", "-p", str(test_csv)])
            assert result.exit_code == 0
            
            # Try to create another with the same name
            result = runner.invoke(cli, ["create", "csv", "test", "-p", str(test_csv)])
            assert result.exit_code == 1
            assert "already exists" in result.output
    
    def test_track_csv_with_json(self, runner: CliRunner, tmp_path: Path):
        """
        Test adding JSON data to a CSV tracker.
        """
        csv_path = tmp_path / "test.csv"
        csv_path.write_text("time,value\n")
        
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["create", "csv", "test", "-p", str(csv_path)])
            assert result.exit_code == 0
            
            result = runner.invoke(cli, ["track", "test", '{"time": "2024-01-01", "value": "100"}'])
            assert result.exit_code == 0
            
            result = runner.invoke(cli, ["show", "test"])
            assert result.exit_code == 0
            assert "2024-01-01" in result.output
            assert "100" in result.output
    
    def test_track_csv_with_invalid_json(self, runner: CliRunner, tmp_path: Path):
        """
        Test that invalid JSON is rejected for CSV tracker.
        """
        csv_path = tmp_path / "test.csv"
        csv_path.write_text("time,value\n")
        
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["create", "csv", "test", "-p", str(csv_path)])
            assert result.exit_code == 0
            
            result = runner.invoke(cli, ["track", "test", "not-json"])
            assert result.exit_code != 0


@pytest.mark.usefixtures("non_interactive_backend")
class TestPlotting:
    """Tests for plotting functionality."""
    
    def test_plot_csv(self, runner: CliRunner, test_csv: Path):
        """
        Test plotting data from a CSV tracker.
        """
        with runner.isolated_filesystem(), \
             patch('webbrowser.open') as mock_browser:
            # Create a CSV tracker
            result = runner.invoke(cli, ["create", "csv", "test", "-p", str(test_csv)])
            assert result.exit_code == 0
            
            # Plot should work without error
            result = runner.invoke(cli, ["plot", "test", "date", "number"])
            assert result.exit_code == 0
            
            # Check that webbrowser.open was called with a file:// URL
            mock_browser.assert_called_once()
            url = mock_browser.call_args[0][0]  # Get the first positional arg
            assert url.startswith('file://')


class TestTerminalPlotting:
    """Tests for CLI terminal plotting commands."""
    
    def test_plot_terminal_calls_tracker_method(self, runner: CliRunner, test_csv: Path):
        """Test that plot --terminal calls tracker.plot_terminal with correct args."""
        pytest.importorskip("plotext")
        
        with runner.isolated_filesystem(), \
             patch('trackstuff.main.CsvTracker.plot_terminal') as mock_plot:
            
            result = runner.invoke(cli, ["create", "csv", "test", "-p", str(test_csv)])
            assert result.exit_code == 0
            
            result = runner.invoke(cli, ["plot", "--terminal", "test", "time", "number"])
            assert result.exit_code == 0
            
            mock_plot.assert_called_once_with(x='time', y='number')

    def test_plot_terminal_uses_default_columns(self, runner: CliRunner, test_csv: Path):
        """Test that plot --terminal uses first two columns when not specified."""
        pytest.importorskip("plotext")
        
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["create", "csv", "test", "-p", str(test_csv)])
            assert result.exit_code == 0
            
            result = runner.invoke(cli, ["plot", "--terminal", "test"])
            assert result.exit_code == 0
            assert "Using columns: x=date, y=number" in result.output

    def test_plot_terminal_fails_when_tracker_missing(self, runner: CliRunner):
        """Test that plot --terminal exits with error when tracker doesn't exist."""
        pytest.importorskip("plotext")
        
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["plot", "--terminal", "nonexistent", "time", "mass"])
            assert result.exit_code != 0
            assert "Tracker 'nonexistent' not found" in result.output

    def test_plot_fails_with_insufficient_columns(self, runner: CliRunner, tmp_path: Path):
        """Test that plot fails when tracker has fewer than 2 columns."""
        pytest.importorskip("plotext")
        
        with runner.isolated_filesystem():
            csv_path = tmp_path / "single_col.csv"
            csv_path.write_text("value\n10\n20\n30\n")
            
            result = runner.invoke(cli, ["create", "csv", "test", "-p", str(csv_path)])
            assert result.exit_code == 0
            
            result = runner.invoke(cli, ["plot", "--terminal", "test"])
            assert result.exit_code == 1
            assert "must have at least 2 columns" in result.output
