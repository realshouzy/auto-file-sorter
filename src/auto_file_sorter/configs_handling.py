#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Module responsible for handling the JSON configs."""
from __future__ import annotations

__all__: list[str] = ["read_from_configs", "write_to_configs"]

import json
import logging
from typing import Final

from auto_file_sorter.constants import CONFIG_LOG_LEVEL, CONFIGS_LOCATION, EXIT_FAILURE

_CONFIGS_HANDLING_LOGGER: Final[logging.Logger] = logging.getLogger(__name__)


def read_from_configs() -> dict[str, str]:
    """Function wrapping ``open`` for reading from ``configs.json``."""
    try:
        _CONFIGS_HANDLING_LOGGER.debug("Opening %s", CONFIGS_LOCATION)
        with open(CONFIGS_LOCATION, "r", encoding="utf-8") as json_file:
            _CONFIGS_HANDLING_LOGGER.debug("Loading %s", json_file)
            configs_dict: dict[str, str] = json.load(json_file)
    except FileNotFoundError as no_file_err:
        _CONFIGS_HANDLING_LOGGER.critical(
            "Unable to find 'configs.json', falling back to an empty configuration",
        )
        configs_dict = {}
        write_to_configs(configs_dict)
        raise SystemExit(EXIT_FAILURE) from no_file_err
    except PermissionError as perm_err:
        _CONFIGS_HANDLING_LOGGER.critical(
            "Permission denied to open and read from '%s'",
            CONFIGS_LOCATION,
        )
        raise SystemExit(EXIT_FAILURE) from perm_err
    except OSError as os_err:
        _CONFIGS_HANDLING_LOGGER.critical(
            "I/O-related error occurred while opening and reading from '%s'",
            CONFIGS_LOCATION,
        )
        raise SystemExit(EXIT_FAILURE) from os_err
    except json.JSONDecodeError as json_decode_err:
        _CONFIGS_HANDLING_LOGGER.critical(
            "Given JSON file is not correctly formatted: %s",
            CONFIGS_LOCATION,
        )
        raise SystemExit(EXIT_FAILURE) from json_decode_err
    except Exception as err:
        _CONFIGS_HANDLING_LOGGER.exception("Unexpected %s", err.__class__.__name__)
        raise SystemExit(EXIT_FAILURE) from err
    _CONFIGS_HANDLING_LOGGER.log(
        CONFIG_LOG_LEVEL,
        "Read from %s",
        CONFIGS_LOCATION,
    )
    return configs_dict


def write_to_configs(new_configs: dict[str, str]) -> None:
    """Function wrapping ``open`` for writing to ``configs.json``."""
    try:
        _CONFIGS_HANDLING_LOGGER.debug("Opening '%s'", CONFIGS_LOCATION)
        with open(CONFIGS_LOCATION, "w", encoding="utf-8") as json_file:
            _CONFIGS_HANDLING_LOGGER.debug("Dumping: %s", new_configs)
            json.dump(new_configs, json_file, indent=4)
    except TypeError as type_err:
        _CONFIGS_HANDLING_LOGGER.critical(
            "Given JSON file is not correctly configured: %s",
            CONFIGS_LOCATION,
        )
        raise SystemExit(EXIT_FAILURE) from type_err
    except PermissionError as perm_err:
        _CONFIGS_HANDLING_LOGGER.critical(
            "Permission denied to open and read from '%s'",
            CONFIGS_LOCATION,
        )
        raise SystemExit(EXIT_FAILURE) from perm_err
    except FileNotFoundError as no_file_err:
        _CONFIGS_HANDLING_LOGGER.critical(
            "Unable to find '%s'",
            CONFIGS_LOCATION,
        )
        raise SystemExit(EXIT_FAILURE) from no_file_err
    except OSError as os_err:
        _CONFIGS_HANDLING_LOGGER.critical(
            "I/O-related error occurred while opening and reading from '%s'",
            CONFIGS_LOCATION,
        )
        raise SystemExit(EXIT_FAILURE) from os_err
    except Exception as err:
        _CONFIGS_HANDLING_LOGGER.exception("Unexpected %s", err.__class__.__name__)
        raise SystemExit(EXIT_FAILURE) from err
    _CONFIGS_HANDLING_LOGGER.log(
        CONFIG_LOG_LEVEL,
        "Added new extension configuration: %s",
        new_configs,
    )
