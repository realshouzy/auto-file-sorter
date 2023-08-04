"""Module responsible for handling the JSON configs."""
from __future__ import annotations

__all__: list[str] = ["read_from_configs", "write_to_configs"]

import json
import logging
from typing import TYPE_CHECKING

from auto_file_sorter.constants import (
    CONFIG_LOG_LEVEL,
    DEFAULT_CONFIGS_LOCATION,
    EXIT_FAILURE,
)

if TYPE_CHECKING:
    from pathlib import Path

configs_handling_logger: logging.Logger = logging.getLogger(__name__)


def read_from_configs(*, configs: Path = DEFAULT_CONFIGS_LOCATION) -> dict[str, str]:
    """Warp ``open`` for easy reading from ``configs.json``."""
    try:
        configs_handling_logger.debug("Reading from '%s'", configs)
        configs_dict: dict[str, str] = json.loads(configs.read_text(encoding="utf-8"))
    except FileNotFoundError as no_file_err:
        configs_handling_logger.critical(
            "Unable to find 'configs.json', falling back to an empty configuration",
        )
        configs_dict = {}
        write_to_configs(configs_dict, configs=configs)
        raise SystemExit(EXIT_FAILURE) from no_file_err
    except PermissionError as perm_err:
        configs_handling_logger.critical(
            "Permission denied to open and read from '%s'",
            configs,
        )
        raise SystemExit(EXIT_FAILURE) from perm_err
    except OSError as os_err:
        configs_handling_logger.critical(
            "I/O-related error occurred while opening and reading from '%s'",
            configs,
        )
        raise SystemExit(EXIT_FAILURE) from os_err
    except json.JSONDecodeError as json_decode_err:
        configs_handling_logger.critical(
            "Given JSON file is not correctly formatted: %s",
            configs,
        )
        raise SystemExit(EXIT_FAILURE) from json_decode_err
    except Exception as err:
        configs_handling_logger.exception("Unexpected %s", err.__class__.__name__)
        raise SystemExit(EXIT_FAILURE) from err
    configs_handling_logger.log(
        CONFIG_LOG_LEVEL,
        "Read from %s",
        configs,
    )
    return configs_dict


def write_to_configs(
    new_configs: dict[str, str],
    *,
    configs: Path = DEFAULT_CONFIGS_LOCATION,
) -> None:
    """Warp ``open`` for easy writing to ``configs.json``."""
    try:
        configs_handling_logger.debug("Writing to '%s'", configs)
        configs.write_text(json.dumps(new_configs, indent=4), encoding="utf-8")
    except TypeError as type_err:
        configs_handling_logger.critical(
            "Given JSON file is not correctly configured: %s",
            configs,
        )
        raise SystemExit(EXIT_FAILURE) from type_err
    except PermissionError as perm_err:
        configs_handling_logger.critical(
            "Permission denied to open and read from '%s'",
            configs,
        )
        raise SystemExit(EXIT_FAILURE) from perm_err
    except FileNotFoundError as no_file_err:
        configs_handling_logger.critical(
            "Unable to find '%s'",
            configs,
        )
        raise SystemExit(EXIT_FAILURE) from no_file_err
    except OSError as os_err:
        configs_handling_logger.critical(
            "I/O-related error occurred while opening and reading from '%s'",
            configs,
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
