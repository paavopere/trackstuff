from pathlib import Path
from unittest.mock import patch

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
            result = runner.invoke(cli, ["plot", "test", "time", "number"])
            assert result.exit_code == 0
            
            # Check that webbrowser.open was called with a file:// URL
            mock_browser.assert_called_once()
            url = mock_browser.call_args[0][0]  # Get the first positional arg
            assert url.startswith('file://')


class TestTerminalPlotting:
    """Tests for terminal-based plotting with plotext."""
    
    def test_plot_terminal_succeeds_when_tracker_exists(self, runner: CliRunner, test_csv: Path):
        """
        Test that plot --terminal returns exit code 0 when tracker exists.
        """
        pytest.importorskip("plotext")
        
        with runner.isolated_filesystem():
            # Create a CSV tracker
            result = runner.invoke(cli, ["create", "csv", "test", "-p", str(test_csv)])
            assert result.exit_code == 0
            
            # Plot in terminal should succeed
            result = runner.invoke(cli, ["plot", "--terminal", "test", "time", "number"])
            assert result.exit_code == 0

    def test_plot_terminal_uses_default_columns(self, runner: CliRunner, test_csv: Path):
        """
        Test that plot --terminal uses first two columns when x and y not specified.
        """
        pytest.importorskip("plotext")
        
        with runner.isolated_filesystem():
            # Create a CSV tracker
            result = runner.invoke(cli, ["create", "csv", "test", "-p", str(test_csv)])
            assert result.exit_code == 0
            
            # Plot without specifying columns
            result = runner.invoke(cli, ["plot", "--terminal", "test"])
            assert result.exit_code == 0
            assert "Using columns: x=time, y=number" in result.output

    def test_plot_terminal_fails_when_tracker_missing(self, runner: CliRunner):
        """
        Test that plot --terminal exits with error when tracker doesn't exist.
        """
        pytest.importorskip("plotext")
        
        with runner.isolated_filesystem():
            # Try to plot a non-existent tracker
            result = runner.invoke(cli, ["plot", "--terminal", "nonexistent", "time", "mass"])
            assert result.exit_code != 0
            assert "Tracker 'nonexistent' not found" in result.output
