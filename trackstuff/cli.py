import logging
import tempfile
import webbrowser
from pathlib import Path

import click

from trackstuff.main import State, SimpleTracker, CsvTracker


_log = logging.getLogger(__name__)


def get_tracker_or_exit(state: State, name: str):
    """Get a tracker by name or exit with error message if not found."""
    try:
        return state.get_tracker(name)
    except KeyError:
        click.echo(f"Tracker '{name}' not found", err=True)
        raise SystemExit(1)


@click.group()
def cli(debug=False):
    if debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logging.basicConfig(level=log_level)
    _log.debug("Logging has been configured")
    pass


@cli.command()
@click.argument("name")
@click.argument("data")
def track(name, data):
    state = State.load()
    tracker = get_tracker_or_exit(state, name)
    tracker.add_entry(data)
    state.save()


@cli.group()
def create():
    pass


@create.command(name="simple")
@click.argument("name")
def create_simple(name):
    """Create a simple tracker"""
    _log.debug(f"create_simple({name=})")
    state = State.load()
    tracker = SimpleTracker(name=name)
    state.add_tracker(tracker)
    state.save()



@create.command(name="csv")
@click.argument("name")
@click.option("--path", "-p", type=click.Path(path_type=Path))
def create_csv(name, path: Path):
    """Create a CSV-backed tracker"""
    _log.debug(f"create_csv({name=}, {path=})")
    state = State.load()
    tracker = CsvTracker(name, path)
    # TODO validate path: unique, exists?
    state.add_tracker(tracker)
    state.save()


@cli.command()
def list():
    state = State.load()
    trackers = state._state_dict.get("trackers", {})
    for t in sorted(trackers, key=lambda x: x.name):
        print(t)


@cli.command()
@click.argument("name")
def show(name):
    state = State.load()
    tracker = get_tracker_or_exit(state, name)
    click.echo(tracker.entries)

@cli.command()
@click.argument("name")
@click.argument("x", type=str, required=False)
@click.argument("y", type=str, required=False)
@click.option("--terminal", is_flag=True, help="Plot in terminal using ASCII characters")
def plot(name: str, x: str | None, y: str | None, terminal: bool):
    """Plot data from a tracker in the default web browser or terminal.
    
    If x and y are not provided, uses the first two columns from the tracker.
    """
    state = State.load()
    tracker = get_tracker_or_exit(state, name)
    
    if x is None or y is None:
        columns = tracker.columns
        if len(columns) < 2:
            click.echo("Error: Tracker must have at least 2 columns", err=True)
            raise SystemExit(1)
        x = columns[0]
        y = columns[1]
        click.echo(f"Using columns: x={x}, y={y}")
    
    if terminal:
        tracker.plot_terminal(x=x, y=y)
    else:
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp:
            plot_path = Path(temp.name)
            tracker.create_plot(x=x, y=y, path=plot_path)
            webbrowser.open(f"file://{plot_path}")

if __name__ == "__main__":
    cli()  # pragma: no cover
