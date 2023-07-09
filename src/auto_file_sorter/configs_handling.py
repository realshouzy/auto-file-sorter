#!/usr/bin/env python3
"""Module responsible for handling the JSON configs."""
from __future__ import annotations

__all__: list[str] = ["read_from_configs", "write_to_configs"]

import json
import logging

from auto_file_sorter.constants import CONFIG_LOG_LEVEL, CONFIGS_LOCATION, EXIT_FAILURE

configs_handling_logger: logging.Logger = logging.getLogger(__name__)


def read_from_configs() -> dict[str, str]:
    """Warp ``open`` for easy reading from ``configs.json``."""
    try:
        configs_handling_logger.debug("Opening %s", CONFIGS_LOCATION)
        with CONFIGS_LOCATION.open(mode="r", encoding="utf-8") as json_file:
            configs_handling_logger.debug("Loading %s", json_file)
            configs_dict: dict[str, str] = json.load(json_file)
    except FileNotFoundError as no_file_err:
        configs_handling_logger.critical(
            "Unable to find 'configs.json', falling back to an empty configuration",
        )
        configs_dict = {}
        write_to_configs(configs_dict)
        raise SystemExit(EXIT_FAILURE) from no_file_err
    except PermissionError as perm_err:
        configs_handling_logger.critical(
            "Permission denied to open and read from '%s'",
            CONFIGS_LOCATION,
        )
        raise SystemExit(EXIT_FAILURE) from perm_err
    except OSError as os_err:
        configs_handling_logger.critical(
            "I/O-related error occurred while opening and reading from '%s'",
            CONFIGS_LOCATION,
        )
        raise SystemExit(EXIT_FAILURE) from os_err
    except json.JSONDecodeError as json_decode_err:
        configs_handling_logger.critical(
            "Given JSON file is not correctly formatted: %s",
            CONFIGS_LOCATION,
        )
        raise SystemExit(EXIT_FAILURE) from json_decode_err
    except Exception as err:
        configs_handling_logger.exception("Unexpected %s", err.__class__.__name__)
        raise SystemExit(EXIT_FAILURE) from err
    configs_handling_logger.log(
        CONFIG_LOG_LEVEL,
        "Read from %s",
        CONFIGS_LOCATION,
    )
    return configs_dict


def write_to_configs(new_configs: dict[str, str]) -> None:
    """Warp ``open`` for easy writing to ``configs.json``."""
    try:
        configs_handling_logger.debug("Opening '%s'", CONFIGS_LOCATION)
        with CONFIGS_LOCATION.open(mode="w", encoding="utf-8") as json_file:
            configs_handling_logger.debug("Dumping: %s", new_configs)
            json.dump(new_configs, json_file, indent=4)
    except TypeError as type_err:
        configs_handling_logger.critical(
            "Given JSON file is not correctly configured: %s",
            CONFIGS_LOCATION,
        )
        raise SystemExit(EXIT_FAILURE) from type_err
    except PermissionError as perm_err:
        configs_handling_logger.critical(
            "Permission denied to open and read from '%s'",
            CONFIGS_LOCATION,
        )
        raise SystemExit(EXIT_FAILURE) from perm_err
    except FileNotFoundError as no_file_err:
        configs_handling_logger.critical(
            "Unable to find '%s'",
            CONFIGS_LOCATION,
        )
        raise SystemExit(EXIT_FAILURE) from no_file_err
    except OSError as os_err:
        configs_handling_logger.critical(
            "I/O-related error occurred while opening and reading from '%s'",
            CONFIGS_LOCATION,
        )
        raise SystemExit(EXIT_FAILURE) from os_err
    except Exception as err:
        configs_handling_logger.exception("Unexpected %s", err.__class__.__name__)
        raise SystemExit(EXIT_FAILURE) from err
    configs_handling_logger.log(
        CONFIG_LOG_LEVEL,
        "Added new extension configuration: %s",
        new_configs,
    )
