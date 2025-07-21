import logging
import tempfile
import time
import webbrowser
from contextlib import contextmanager
from pathlib import Path
from pprint import pformat

import click

from trackstuff.main import State, SimpleTracker, CsvTracker


_log = logging.getLogger(__name__)


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
    tracker = state.get_tracker(name)
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
    entries = state.get_tracker(name).entries
    click.echo(entries)

@cli.command()
@click.argument("name")
@click.argument("x", type=str)
@click.argument("y", type=str)
def plot(name: str, x: str, y: str):
    """Plot data from a tracker in the default web browser."""
    state = State.load()
    tracker = state.get_tracker(name)
    
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp:
        plot_path = Path(temp.name)
        tracker.create_plot(x=x, y=y, path=plot_path)
        webbrowser.open(f"file://{plot_path}")

if __name__ == "__main__":
    cli()  # pragma: no cover
