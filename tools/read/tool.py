"""Read the contents of a file, given a repo-relative path."""

from pathlib import Path


def run(path: str) -> str:
    try:
        return Path(path).read_text()
    except FileNotFoundError:
        return f"Error: file not found: {path}"
