#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Module responsible for handling the JSON configs."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Final, NamedTuple, TypeAlias

__all__: list[str] = ["Configs", "read_from_configs", "write_to_configs"]

_ConfigsDict: TypeAlias = dict[str, dict[str, str | int]]

PROGRAM_LOCATION: Final[Path] = Path(__file__).resolve().parent
_CONFIGS_LOCATION: Final[Path] = PROGRAM_LOCATION.joinpath("configs.json")

_DEFAULT_CONFIGS: Final[_ConfigsDict] = {
    "logging": {
        "level": logging.INFO,
        "format": "%(name)s [%(levelname)s] %(asctime)s - %(message)s",
    },
    "extension_paths": {},
}


class Configs(NamedTuple):
    """Class for configs."""

    level: int
    format: str  # noqa: A003
    extension_paths: dict[str, str]


# pylint: disable=broad-exception-caught


def read_from_configs() -> Configs:
    """Function wrapping ``open`` for reading from ``configs.json`` with exception handling and logging."""
    json_logger: logging.Logger = logging.getLogger(read_from_configs.__name__)
    try:
        json_logger.debug("Opening %s", _CONFIGS_LOCATION)
        with open(_CONFIGS_LOCATION, "r", encoding="utf-8") as json_file:
            json_logger.debug("Loading %s", json_file)
            config_dict: _ConfigsDict = json.load(json_file)
        json_logger.info("Read from %s", _CONFIGS_LOCATION)
    except FileNotFoundError:
        json_logger.info(
            "Unable to find 'configs.json', falling back to the default configuration",
        )
        config_dict = _DEFAULT_CONFIGS
    except json.JSONDecodeError as json_decode_err:
        json_logger.critical(
            "Given JSON file is not correctly formatted: %s",
            _CONFIGS_LOCATION,
        )
        raise SystemExit(1) from json_decode_err
    except Exception as err:
        json_logger.exception("Unexpected %s", err.__class__.__name__)
        raise SystemExit(1) from err

    try:
        level: int = config_dict["logging"]["level"]  # type: ignore
        format_: str = config_dict["logging"]["format"]  # type: ignore
        extension_paths: dict[str, str] = config_dict["extension_paths"]  # type: ignore
        return Configs(level, format_, extension_paths)
    except KeyError as key_err:
        json_logger.critical(
            "Given JSON file is not correctly configured: %s",
            _CONFIGS_LOCATION,
        )
        raise SystemExit(1) from key_err
    except Exception as err:
        json_logger.exception("Unexpected %s", err.__class__.__name__)
        raise SystemExit(1) from err


def write_to_configs(new_configs: Configs) -> None:
    """Function wrapping ``open`` for writing to ``configs.json`` with exception handling and logging."""
    json_logger: logging.Logger = logging.getLogger(write_to_configs.__name__)
    new_configs_dict: _ConfigsDict = {
        "logging": {
            "level": new_configs.level,
            "format": new_configs.format,
        },
        "extension_paths": new_configs.extension_paths,  # type: ignore
    }

    try:
        json_logger.debug("Opening 'extension.json'")
        with open(_CONFIGS_LOCATION, "w", encoding="utf-8") as json_file:
            json_logger.debug("Dumping: %s", new_configs_dict)
            json.dump(new_configs_dict, json_file, indent=4)
        json_logger.info(
            "Added new extension configuration: '%s'",
            new_configs,
        )
    except KeyError as key_err:
        json_logger.critical(
            "Given JSON file is not correctly configured: %s",
            _CONFIGS_LOCATION,
        )
        raise SystemExit(1) from key_err
    except Exception as err:
        json_logger.exception("Unexpected %s", err.__class__.__name__)
        raise SystemExit(1) from err
