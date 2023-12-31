# Wordle Solver for Mum
Tool to help with solving the daily wordle.

## User
### Run wordle_solver.
1. Open terminal
2. Navigate to directory containing wordle_solver.exe
3. Run command `wordle_solver.exe`

## Developer
### Setup
```
poetry shell
poetry install
```

### Formatting
```ruff format```

### Type checking
```pyright```

### Linting
```
ruff check --fix
pylint wordle_solver.py
```

### Packaging
```
pyinstaller -F -i wordle_icon.ico .\wordle_solver.py
```