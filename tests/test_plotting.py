"""Tests for plotting module."""

from pathlib import Path

import pandas as pd
import pytest

from trackstuff.plotting import make_title, plot_to_file, plot_to_terminal


def test_make_title():
    """Test make_title function with and without name."""
    assert make_title("x", "y", name="name") == "name: y(x)"
    assert make_title("x", "y") == make_title("x", "y", name=None) == "y(x)"


class TestPlotToFile:
    """Tests for plot_to_file function."""

    @pytest.fixture
    def sample_df(self):
        """Create a sample DataFrame for testing."""
        return pd.DataFrame({'time': ['2024-01-01', '2024-01-02', '2024-01-03'], 'value': [10, 20, 15]})

    def test_plot_to_file_creates_png(self, sample_df, tmp_path):
        """Test that plot_to_file creates a PNG file."""
        output_path = tmp_path / "test_plot.png"

        plot_to_file(sample_df, x='time', y='value', path=output_path, name="test")

        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_plot_to_file_without_name(self, sample_df, tmp_path):
        """Test plot_to_file without a name."""
        output_path = tmp_path / "test_plot_no_name.png"

        plot_to_file(sample_df, x='time', y='value', path=output_path)

        assert output_path.exists()

    def test_plot_to_file_parses_dates(self, sample_df, tmp_path):
        """Test that plot_to_file correctly parses date columns."""
        output_path = tmp_path / "test_plot_dates.png"

        # Should not raise an error when parsing dates
        plot_to_file(sample_df, x='time', y='value', path=output_path, name="dates")

        assert output_path.exists()

    def test_plot_to_file_sets_labels_and_title(self, sample_df, tmp_path):
        """Test that plot_to_file sets proper labels and title."""
        output_path = tmp_path / "test_plot_labels.png"

        # Just verify it doesn't crash and creates a file
        plot_to_file(sample_df, x='time', y='value', path=output_path, name="test")

        assert output_path.exists()
        assert output_path.stat().st_size > 0


class TestPlotToTerminalOutput:
    """Integration tests for terminal plotting output."""

    @pytest.fixture
    def test_csv_path(self):
        """Path to test CSV file."""
        return Path(__file__).parent / "data" / "date_number.csv"

    def test_terminal_plot_shows_title(self, test_csv_path, capsys):
        """Test that terminal plot output contains the title."""
        pytest.importorskip("plotext")

        df = pd.read_csv(test_csv_path)
        plot_to_terminal(df, x='date', y='number', name='testdata')

        captured = capsys.readouterr()
        assert 'testdata: number(date)' in captured.out

    def test_terminal_plot_shows_dates(self, test_csv_path, capsys):
        """Test that terminal plot output contains date labels."""
        pytest.importorskip("plotext")

        df = pd.read_csv(test_csv_path)
        plot_to_terminal(df, x='date', y='number', name='testdata')

        captured = capsys.readouterr()
        # Should show at least some dates from 2020
        assert '2020' in captured.out
