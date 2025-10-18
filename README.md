# trackstuff

Track stuff and plot it.

## Installation

```bash
uv sync
```

## Usage

### Create Trackers

Create a simple tracker:
```bash
uv run -m trackstuff.cli create simple my-simple-tracker
```

Create a CSV-backed tracker (use an existing file that has 2 columns):
```bash
uv run -m trackstuff.cli create csv my-csv-tracker -p my-csv-tracker.csv
```

### Add Data

Track data to a simple tracker:
```bash
uv run -m trackstuff.cli track my-simple-tracker 123
uv run -m trackstuff.cli track my-simple-tracker abc
```

Tracking data to a CSV-backed tracker doesn't work yet, lol.

### View Data

Show entries from a tracker:
```bash
uv run -m trackstuff.cli show mytracker
```

List all trackers:
```bash
uv run -m trackstuff.cli list
```

### Plot Data

Plot in browser (PNG):
```bash
# plot first 2 columns
uv run -m trackstuff.cli plot my-csv-tracker
# specify X and Y columns
uv run -m trackstuff.cli plot my-csv-tracker columnX columnY
```

Plot in terminal (ASCII):
```bash
uv run -m trackstuff.cli plot --terminal my-csv-tracker
```

Plot using default columns (first two):
```bash
uv run -m trackstuff.cli plot --terminal hptrack
```

## Development

Run tests and checks:
```bash
uv run pytest
uv run mypy
uv run ruff check
```

