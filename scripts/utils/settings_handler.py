# -*- coding: UTF-8 -*-
"""Context manager for settings handling."""
from __future__ import annotations
from typing import Iterator, NoReturn, TypeAlias
from pathlib import Path

from contextlib import contextmanager
import sys
import json
import PySimpleGUI as sg

Settings: TypeAlias = dict[str, dict[str, Path | int | str]]


@contextmanager
def open_settings() -> Iterator[Settings] | NoReturn:
    """
    Function that creates context manager for easy access to the settings json file with exception handling.

    :rtype: Iterator[dict[str, dict[str, Path | int | str]]]
    """
    try:
        file = open("settings.json", "r", encoding="UTF-8")
        yield json.load(file)
    except FileNotFoundError:
        sg.PopupError(
            f"{__file__}:\nSettings json file not found. Must be located in the same directory as the executable.",
            title="FileSorter",
        )
    except KeyError:
        sg.PopupError(
            f"{__file__}:\nSettings json file is not correctly configured.",
            title="FileSorter",
        )
        sys.exit(1)
    except Exception as ex:
        sg.PopupError(f"Unexpected {type(ex).__name__} -> check log for more info.")
    finally:
        if "file" in locals():  # avoid UnboundLocalError if file never was opend
            file.close()
        else:
            sys.exit(1)
