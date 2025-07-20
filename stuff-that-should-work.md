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
>>> rm foo.csv
>>> cp hp-bup.csv bar.csv
>>> python -m trackstuff.cli create csv bar -p foo.csv
>>> python -m trackstuff.cli show bar
```

_TODO implement adding data to CSV_

_TODO implement visualizing time-series data_

Type-checking

```sh
mypy --enable-incomplete-feature=NewGenericSyntax .
```

_TODO add more linters_
