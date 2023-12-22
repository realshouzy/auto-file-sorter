"""Module containing useful utilities."""
from __future__ import annotations

__all__: list[str] = ["resolved_path_from_str"]

from pathlib import Path


def resolved_path_from_str(path_as_str: str) -> Path:
    """Return the absolute path given a string of a path."""
    return Path(path_as_str.strip()).resolve()
