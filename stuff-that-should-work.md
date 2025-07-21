Create simple tracker, add data, show data

```sh
>>> rm state.json
>>> python -m trackstuff.cli create simple foo
>>> python -m trackstuff.cli track foo 123
>>> python -m trackstuff.cli track foo abc
>>> python -m trackstuff.cli show foo
['123', 'abc']
```

Create tracker from existing csv file and show data:

```sh
>>> rm hptrack.csv
>>> cp hp-bup.csv hptrack.csv
>>> python -m trackstuff.cli create csv hptrack -p hptrack.csv
>>> python -m trackstuff.cli show hptrack
```

_TODO implement adding data to CSV_

Visualize time-series data from CSV:

```sh
>>> python -m trackstuff.cli plot hptrack time mass
```

Type-checking:
```sh
mypy .
```

Testing with coverage:
```sh
pytest
```

_TODO add more linters_
