from pathlib import Path


def run(path: str) -> str:
    """Read the contents of a file, given a repo-relative path."""
    try:
        return Path(path).read_text()
    except FileNotFoundError:
        return f"Error: file not found: {path}"
