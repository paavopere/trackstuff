import csv
import json
from pathlib import Path

import pandas as pd

from trackstuff.plotting import plot_to_file, plot_to_terminal
from trackstuff.trackers import Tracker


class CsvTracker(Tracker):
    def __init__(self, name: str, path: Path):
        self.name = name
        self.path = path.absolute()

    def to_dict(self):
        return {"kind": "csv", "name": self.name, "path": str(self.path)}

    def add_entry(self, entry: str) -> None:
        entry_dict = json.loads(entry)
        if not isinstance(entry_dict, dict):
            raise TypeError("Entry must be a JSON that parses to a dict")

        columns = self.columns
        if set(entry_dict.keys()) != set(columns):
            raise ValueError(f"Entry keys {set(entry_dict.keys())} do not match CSV columns {set(columns)}")

        # Ensure file ends with newline before appending
        with open(self.path, 'r+') as f:
            f.seek(0, 2)  # Go to end of file
            f.seek(f.tell() - 1)  # Go to last character
            last_char = f.read(1)
            if last_char != '\n':
                f.write('\n')

        with open(self.path, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writerow(entry_dict)

    @property
    def columns(self):
        with open(self.path) as f:
            return csv.DictReader(f).fieldnames

    @property
    def entries(self):
        with open(self.path) as f:
            return list(csv.DictReader(f))

    def to_dataframe(self) -> pd.DataFrame:
        """
        Load the CSV data as a pandas DataFrame.
        """
        return pd.read_csv(self.path)

    def create_plot(self, x: str, y: str, path: Path) -> None:
        """
        Create a plot from the CSV data and save it to the specified path.
        """
        df = self.to_dataframe()
        plot_to_file(df, x=x, y=y, path=path, name=self.name)

    def plot_terminal(self, x: str, y: str) -> None:
        """
        Plot data in the terminal using plotext.
        """
        df = self.to_dataframe()
        plot_to_terminal(df, x=x, y=y, name=self.name)
