Create simple tracker, add data, show data

```sh
rm state.json
uv run -m trackstuff.cli create simple foo
uv run -m trackstuff.cli track foo 123
uv run -m trackstuff.cli track foo abc
uv run -m trackstuff.cli show foo
```

should show:
```
['123', 'abc']
```

Create tracker from existing csv file and show data:

```sh
rm hptrack.csv
cp hp-bup.csv hptrack.csv
uv run -m trackstuff.cli create csv hptrack -p hptrack.csv
uv run -m trackstuff.cli show hptrack
```

_TODO implement adding data to CSV_

Visualize time-series data from CSV:

```sh
uv run -m trackstuff.cli plot hptrack time mass
```

Checks:

```sh
uv run pytest
uv run mypy
uv run ruff check
```

