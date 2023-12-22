"""Tests for ``auto_file_sorter.utils``."""
from __future__ import annotations

import platform
from pathlib import Path

import pytest

from auto_file_sorter.utils import resolved_path_from_str

# pylint: disable=C0116


@pytest.mark.skipif(
    platform.system() != "Windows",
    reason="Test behavior on Windows-systems",
)
@pytest.mark.parametrize(
    ("path_as_str", "expected_path"),
    (
        pytest.param(
            "/path/to/some/file.txt",
            Path("C:/path/to/some/file.txt"),
            id="regular_str",
        ),
        pytest.param(
            "  /path/to/some/file.txt  ",
            Path("C:/path/to/some/file.txt"),
            id="trailing_whitespaces_str",
        ),
    ),
)
def test_resolved_path_from_str_windows(
    path_as_str: str,
    expected_path: Path,
) -> None:  # pragma: win32 cover
    assert resolved_path_from_str(path_as_str) == expected_path


@pytest.mark.skipif(
    platform.system() != "Linux" and platform.system() != "Darwin",
    reason="Test behavior on Posix systems",
)
@pytest.mark.parametrize(
    ("path_as_str", "expected_path"),
    (
        pytest.param(
            "/path/to/some/file.txt",
            Path("/path/to/some/file.txt"),
            id="regular_str",
        ),
        pytest.param(
            "  /path/to/some/file.txt  ",
            Path("/path/to/some/file.txt"),
            id="trailing_whitespaces_str",
        ),
    ),
)
def test_resolved_path_from_str_posix(
    path_as_str: str,
    expected_path: Path,
) -> None:  # pragma: posix cover
    assert resolved_path_from_str(path_as_str) == expected_path
