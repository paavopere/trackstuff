# trackstuff

Track stuff and plot it.

## Installation

```bash
uv sync
```

To use `trackstuff` directly without prefixing `uv run`, activate the virtual environment:
```bash
source .venv/bin/activate
```

To deactivate later:
```bash
deactivate
```

## Usage

### Create Trackers

Create a simple tracker:
```bash
trackstuff create simple my-simple-tracker
```

Create a CSV-backed tracker from an existing CSV file:
```bash
trackstuff create csv weight -p weight.csv
```

Create a new CSV tracker by specifying columns:
```bash
trackstuff create csv weight -p weight.csv --columns "date,weight"
```

Create a new CSV tracker interactively:
```bash
trackstuff create csv weight -p weight.csv --interactive
# You'll be prompted to enter column names one by one
```

### Add Data

Track data to a simple tracker:
```bash
trackstuff track my-simple-tracker 123
trackstuff track my-simple-tracker abc
```

Track data to a CSV tracker with JSON:
```bash
trackstuff track weight '{"date": "2024-01-15", "weight": "75.5"}'
```

Track data to a CSV tracker interactively:
```bash
trackstuff track --interactive weight
# You'll be prompted for each column value
```

### View Data

Show entries from a tracker:
```bash
trackstuff show weight
```

List all trackers:
```bash
trackstuff list
```

### Plot Data

Plot in browser (PNG):
```bash
# Plot first 2 columns
trackstuff plot weight
# Specify X and Y columns
trackstuff plot weight date weight
```

Plot in terminal (ASCII):
```bash
trackstuff plot --terminal weight
# Or specify columns
trackstuff plot --terminal weight date weight
```

## Development

### Pre-commit Hook

Copy the pre-commit hook to the .git/hooks directory and make it executable. Then checks will run automatically on commit.
```bash
cp pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### Manual Testing

Run all tests and checks manually:
```bash
uv run pytest
uv run mypy trackstuff
uv run ruff check
```

