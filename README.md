# Wordle Helper for Mum
Tool to help with solving the daily wordle.

## User
### Run wordle helper.
1. Open terminal
2. Navigate to directory containing wordle_helper.exe
3. Run command `wordle_helper.exe`

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
pylint wordle_helper.py
```

### Packaging
```
pyinstaller -F -i wordle_icon.ico .\wordle_helper.py
```