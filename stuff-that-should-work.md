```sh
>>> rm state.json
>>> python -m cli create simple foo
>>> python -m cli track foo 123
>>> python -m cli track foo abc
>>> python -m cli show foo
['123', 'abc']
```

```sh
mypy --enable-incomplete-feature=NewGenericSyntax .
```