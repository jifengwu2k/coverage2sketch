# Coverage2Sketch

This code implements a tool to extract "sketches" of Python source files based on coverage data.

In a "sketch":

- Only code that was executed (covered) remains
- Uncovered code is replaced with `...` placeholders
- Consecutive placeholders are collapsed
- Comments and docstrings are removed

This is helpful for:

*   **Understanding Test Coverage:** Quickly visualize which parts of your code are actually executed during testing.
*   **Code Visualization:**  Generate a text-based representation of the code's execution flow.
*   **Debugging:**  Pinpoint areas of code that are not reached or have potential issues.
*   **Code Review:**  Assist in identifying dead code or areas requiring more thorough testing.

## Features

1. **Version Compatibility Handling**:
   - Supports Python 3+
   - Uses different AST node types (`Ellipsis` vs `Constant`) depending on Python version (pre-3.8 vs 3.8+)
   - Uses `astor.to_source` for Python < 3.9 and `ast.unparse` for Python ≥ 3.9

## Installation

```bash
pip install coverage2sketch
```

## Usage as an Executable Module

When used as an executable module (i.e., `python -m coverage2sketch -c .coverage`), the tool outputs Markdown-formatted results showing:

- Each measured file path in backticks
- The code sketch in a Python code block

1. First generate coverage data by running your tests with coverage:
   ```bash
   coverage run -m pytest  # or whatever test command you use
   ```

2. Then generate sketches from the coverage data:
   ```bash
   python -m coverage2sketch -c .coverage | tee sketches.md  # Save to file
   ```

### Command Line Arguments

| Argument | Description |
|----------|-------------|
| `-c`/`--coverage-file` | Path to the `.coverage` data file (default: `.coverage`) |

### Example Output

`/path/to/module.py`:

```python
def covered_function():
    print("This was executed")
    ...

def another_covered_function():
    x = 1
    return x
```

`/path/to/other_module.py`:

```python
class TestedClass:
    def method(self):
        return True
    ...
```

## Usage as a Package

When used as a a package, the function `extract_sketches(coverage_file_path: str) -> Dict[str, str]` returns a dictionary with file path as key and execution trace as value.

```python
from coverage2sketch import extract_sketches

# Example usage
sketches = extract_sketches('/some/directory/.coverage')

# Output the sketches for each module
for file_path, sketch in sketches.items():
    print('File: %s' % file_path)
    print(sketch)
    print('-' * 20)
```

## Contributing

Contributions are welcome!  Please submit pull requests or open issues on [GitHub](<your_github_repo_url>).  (Replace with your actual repository URL.)

## License

This project is licensed under the [MIT License](LICENSE). See the [LICENSE](LICENSE) file for details.
