"""Module responsible for handling the JSON configs."""
from __future__ import annotations

__all__: list[str] = [
    "read_from_configs",
    "write_to_configs",
    "get_selected_configs",
    "add_new_config_to_configs",
    "load_json_file_into_configs",
    "remove_configs",
    "get_extension_paths_from_configs",
]

import json
import logging
from typing import TYPE_CHECKING

from auto_file_sorter.constants import (
    CONFIG_LOG_LEVEL,
    DEFAULT_CONFIGS_LOCATION,
    EXIT_FAILURE,
    EXIT_SUCCESS,
    FILE_EXTENSION_PATTERN,
)
from auto_file_sorter.utils import resolved_path_from_str

if TYPE_CHECKING:
    from pathlib import Path

configs_handling_logger: logging.Logger = logging.getLogger(__name__)


def read_from_configs(*, configs: Path = DEFAULT_CONFIGS_LOCATION) -> dict[str, str]:
    """Read from the given configs JSON file (with error handling)."""
    configs_handling_logger.debug("Reading from '%s'", configs)
    try:
        configs_dict: dict[str, str] = json.loads(configs.read_text(encoding="utf-8"))
    except json.JSONDecodeError as json_decode_err:
        configs_handling_logger.critical(
            "Given JSON file is not correctly formatted: '%s'",
            configs,
        )
        raise SystemExit(EXIT_FAILURE) from json_decode_err
    except FileNotFoundError as no_file_err:
        configs_handling_logger.critical(
            "Unable to find '%s', falling back to an empty configuration",
            configs,
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
    """Write to the given configs JSON file (with error handling)."""
    configs_handling_logger.debug("Writing to '%s'", configs)
    try:
        configs.write_text(json.dumps(new_configs, indent=4), encoding="utf-8")
    except TypeError as type_err:
        configs_handling_logger.critical(
            "Given configs can not be serialized into a JSON formatted: %s",
            new_configs,
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
        "Added new extension configuration %s to '%s'",
        new_configs,
        configs,
    )


def get_selected_configs(
    get_configs: list[str],
    configs: dict[str, str],
) -> dict[str, Path]:
    """Get the selected configs from the configs and store them in a ``dict``."""
    selected_configs: dict[str, Path] = {}

    for config in get_configs:
        extension: str = config.replace(" ", "").lower()

        if FILE_EXTENSION_PATTERN.fullmatch(extension) is None:
            configs_handling_logger.warning(
                "Ignoring invalid extension '%s'",
                extension,
            )
            continue

        if extension not in configs:
            configs_handling_logger.warning(
                "Ignoring '%s', because it is not in the configs",
                extension,
            )
            continue

        try:
            selected_configs[extension] = resolved_path_from_str(configs[extension])
        except KeyError:  # pragma: no cover
            configs_handling_logger.warning(
                "Unable to get the respetive path "
                "of one of the given extensions '%s'",
                extension,
            )
            continue

    if not selected_configs:
        configs_handling_logger.critical("No valid extensions selected")
        configs_handling_logger.debug(
            "repr(selected_configs)=%s",
            repr(selected_configs),
        )
        raise SystemExit(EXIT_FAILURE)
    return selected_configs


def add_new_config_to_configs(new_config: list[str], configs: dict[str, str]) -> int:
    """Add new config to the configs JSON file."""
    configs_handling_logger.debug("new_config=%s", repr(new_config))

    new_extension, new_path = (
        new_config[0].lower().replace(" ", ""),
        new_config[1].strip(),
    )
    configs_handling_logger.debug(
        "Normalized '%s' to '%s'",
        new_config[0],
        new_extension,
    )
    configs_handling_logger.debug(
        "Normalized '%s' to '%s'",
        new_config[1],
        new_path,
    )

    if not new_extension or not new_path:
        configs_handling_logger.critical(
            "Either an empty extension '%s' or an empty path '%s' was specified to add, "
            "which is invalid",
            new_extension,
            new_path,
        )
        return EXIT_FAILURE

    if FILE_EXTENSION_PATTERN.fullmatch(new_extension) is None:
        configs_handling_logger.critical(
            "Given extension '%s' is invalid",
            new_extension,
        )
        return EXIT_FAILURE

    configs_handling_logger.debug("Got '%s': '%s'", new_extension, new_path)

    configs[new_extension] = new_path
    configs_handling_logger.log(
        CONFIG_LOG_LEVEL,
        "Updated '%s': '%s'",
        new_extension,
        new_path,
    )
    return EXIT_SUCCESS


def load_json_file_into_configs(json_file: Path, configs: dict[str, str]) -> int:
    """Load JSON file into configs."""
    configs_handling_logger.debug(
        "json_file='%s'",
        repr(json_file),
    )

    if json_file.suffix.lower() != ".json":
        configs_handling_logger.critical(
            "Configs can only be read from json files",
        )
        return EXIT_FAILURE

    configs_handling_logger.debug("Reading from '%s'", json_file)
    try:
        new_configs_from_json: dict[str, str] = json.loads(
            json_file.read_text(encoding="utf-8"),
        )
    except FileNotFoundError:
        configs_handling_logger.critical(
            "Unable to find '%s'",
            json_file,
        )
        return EXIT_FAILURE
    except PermissionError:
        configs_handling_logger.critical(
            "Permission denied to open and read from '%s'",
            json_file,
        )
        return EXIT_FAILURE
    except OSError:
        configs_handling_logger.critical(
            "Operating system-related error occurred while opening and reading from '%s'",
            json_file,
        )
        return EXIT_FAILURE
    except json.JSONDecodeError:
        configs_handling_logger.critical(
            "Given JSON file is not correctly formatted: '%s'",
            json_file,
        )
        return EXIT_FAILURE
    configs_handling_logger.debug("Read from '%s'", json_file)

    configs.update(new_configs_from_json)
    configs_handling_logger.log(
        CONFIG_LOG_LEVEL,
        "Loaded '%s' into configs",
        json_file,
    )
    return EXIT_SUCCESS


def remove_configs(configs_to_be_removed: list[str], configs: dict[str, str]) -> int:
    """Remove configs from the configs."""
    configs_handling_logger.debug(
        "configs_to_be_removed=%s",
        repr(configs_to_be_removed),
    )

    for config in configs_to_be_removed:
        extension: str = config.replace(" ", "").lower()
        configs_handling_logger.debug("Stripped '%s' to '%s'", config, extension)

        if FILE_EXTENSION_PATTERN.fullmatch(extension) is None:
            configs_handling_logger.warning(
                "Skipping invalid extension: '%s'",
                extension,
            )
            continue

        configs_handling_logger.debug("Normalized '%s' to '%s'", config, extension)

        configs_handling_logger.debug("Removing '%s'", extension)
        try:
            del configs[extension]
        except KeyError:
            configs_handling_logger.warning(
                "Ignoring '%s', because it is not in the configs",
                extension,
            )
            continue
        configs_handling_logger.log(
            CONFIG_LOG_LEVEL,
            "Removed '%s'",
            extension,
        )
    return EXIT_SUCCESS


def get_extension_paths_from_configs(
    configs: dict[str, str],
) -> dict[str, Path]:
    """Get the extension and their respective path from the configs."""
    configs_handling_logger.debug("Resolving extension paths from %s", configs)
    extension_paths: dict[str, Path] = {
        extension: resolved_path_from_str(path_as_str)
        for extension, path_as_str in configs.items()
    }
    configs_handling_logger.info("Got extension paths")
    return extension_paths
