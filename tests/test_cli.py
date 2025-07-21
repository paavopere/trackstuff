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

def test_create_simple_tracker(runner: CliRunner, clean_state: Path):
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

def test_create_csv_tracker(runner: CliRunner, tmp_path: Path):
    """
    Test creating a CSV-backed tracker and showing its data.
    """
    with runner.isolated_filesystem():
        # Create a test CSV with some data
        csv_path = tmp_path / "test.csv"
        csv_path.write_text("time,mass\n2023-01-01,80.5\n2023-01-02,81.0\n")
        
        # Create a tracker out of the CSV file
        result = runner.invoke(cli, ["create", "csv", "test", "-p", str(csv_path)])
        assert result.exit_code == 0
        
        # Show the data
        result = runner.invoke(cli, ["show", "test"])
        assert result.exit_code == 0
        assert "2023-01-01" in result.output
        assert "80.5" in result.output

def test_list_trackers(runner: CliRunner):
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

def test_plot_csv(runner: CliRunner, tmp_path: Path):
    """
    Test plotting data from a CSV tracker.
    """
    with runner.isolated_filesystem(), \
         patch('webbrowser.open') as mock_browser:
        # Create a test CSV
        csv_path = tmp_path / "test.csv"
        csv_path.write_text("time,mass\n2023-01-01,80.5\n2023-01-02,81.0\n")
        
        # Create a CSV tracker
        result = runner.invoke(cli, ["create", "csv", "test", "-p", str(csv_path)])
        assert result.exit_code == 0
        
        # Plot should work without error
        result = runner.invoke(cli, ["plot", "test", "time", "mass"])
        assert result.exit_code == 0
        
        # Check that webbrowser.open was called with a file:// URL
        mock_browser.assert_called_once()
        url = mock_browser.call_args[0][0]  # Get the first positional arg
        assert url.startswith('file://')
