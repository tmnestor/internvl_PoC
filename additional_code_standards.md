## Code Style Guidelines

- Use `ruff` for comprehensive linting and formatting (replaces flake8, isort, pylint, and other tools)
- Python line width must not exceed 108 characters to comply with ruff checker requirements
- All code should follow PEP 8 style guidelines with this line length exception
- Module imports must follow PEP 8 style guidelines, organized in the following order:
  1. Standard library imports
  2. Related third-party imports
  3. Local application/library specific imports
  
  Each group should be separated by a blank line and imports should be alphabetized within each group.
- Imports are properly formatted and sorted according to Python standards
- Use multi-line imports for readability when importing multiple items from the same module

- All imports and variables must be used in the code
- Run `ruff check .` for linting and `ruff format .` for code formatting
- Use `ruff check --fix .` to automatically fix issues where possible

### File and Directory Operations

- **ALWAYS use `pathlib.Path` for file and directory operations** instead of `os.path`
- Use Path objects for cross-platform compatibility and cleaner code
- Prefer Path methods over string concatenation for paths

```python
# Good - Use pathlib
from pathlib import Path

output_path = Path("models") / "classifier"
output_path.mkdir(parents=True, exist_ok=True)
config_file = output_path / "config.json"

if config_file.exists():
    content = config_file.read_text()

# Bad - Don't use os.path or string operations  
import os
output_path = os.path.join("models", "classifier")
os.makedirs(output_path, exist_ok=True)
config_file = os.path.join(output_path, "config.json")
```

- **Directory creation**: Always use `Path.mkdir(parents=True, exist_ok=True)`
- **File existence checks**: Use `Path.exists()` instead of `os.path.exists()`
- **Reading/writing files**: Use `Path.read_text()`, `Path.write_text()` when appropriate
- **Path joining**: Use `/` operator with Path objects instead of `os.path.join()`

## Jupyter Notebook Guidelines

- **Notebook JSON Structure**: When creating or editing .ipynb files manually, ensure all cells include required fields:
  - Code cells must have `execution_count` field (can be `null` for unexecuted cells)
  - All cells must have `metadata`, `outputs`, and `source` fields
  - The notebook is missing required `execution_count` fields for code cells can cause validation errors in GitLab/GitHub
- Use `NotebookEdit` tool for programmatic notebook modifications when possible
- Validate notebook structure after manual JSON edits

## Command Line Interface (CLI) Guidelines
- Add CLI dependencies: `uv add typer rich`
- Use `typer` instead of `argparse` for CLI development
- Use rich for colorful CLI output
- Use `typer` decorators for command definitions
- Use `typer.Option` for options and `typer.Argument` for positional arguments
- Use a dataclass to organise the application wide rich configuration
- Use a separate configuration function to extract argument and option parsing logic 
- Use `rich` to echo the actual system arguments and options inside the configuration function

### Rich Console Configuration

- Use a standardized dataclass for rich console configuration with predefined message styles:

```python
@dataclass
class RichConfig:
    """Configuration for rich console output."""

    console: Console = Console()
    success_style: str = "[bold green]\u2705[/bold green]"
    fail_style: str = "[bold red]\u274C[/bold red]"
    warning_style: str = "[bold yellow]\u26A0[/bold yellow]"
    info_style: str = "[bold blue]ℹ[/bold blue]"
```

- Use these predefined styles consistently throughout the application:
  - `success_style` for successful operations (✅)
  - `fail_style` for errors and failures (❌)
  - `warning_style` for warnings and cautions (⚠️)
  - `info_style` for informational messages (ℹ️)
- Example usage: `console.print(f"{rich_config.success_style} Operation completed successfully")`

  ## Environment-Specific Shell Configuration

  **Important**: This system has custom shell aliases that affect command behavior:

  - **`ls` command**: Aliased to `eza --color=auto --group-directories-first 2>/dev/null || ls --color=auto`
    - The `ls` command uses `eza` (modern ls replacement) with fallback to regular `ls`
    - This may cause unexpected behavior in bash commands when using `ls` for directory listings
    - **Workaround**: Use `\ls` to bypass the alias, `/bin/ls` for direct command, or prefer the `LS` tool for directory operations
    - **Claude Code**: When using the Bash tool for directory listings, be aware that `ls` may not behave as expected. Use the `LS` tool instead for reliable directory operations.

  ### Additional Environment Notes

  - **Shell**: The system uses custom aliases that may affect standard command behavior
  - **Git**: Has custom git alias configuration that may show `git:1: command not found: _autoload_git_aliases` warnings (these can be ignored)
  - **Directory Navigation**: Standard `cd` and path operations work normally, but directory listing commands should use the `LS` tool when precision is required
