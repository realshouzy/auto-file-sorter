"""Module responsible for handling the args."""
from __future__ import annotations

__all__: list[str] = [
    "handle_write_args",
    "handle_read_args",
    "handle_track_args",
    "handle_locations_args",
]

import json
import logging
import os.path
import platform
import re
import sys
from pathlib import Path
from time import sleep
from typing import TYPE_CHECKING

from watchdog.observers import Observer

from auto_file_sorter.configs_handling import read_from_configs, write_to_configs
from auto_file_sorter.constants import (
    CONFIG_LOG_LEVEL,
    EXIT_FAILURE,
    EXIT_SUCCESS,
    FILE_EXTENSION_PATTERN,
)
from auto_file_sorter.event_handling import OnModifiedEventHandler

if TYPE_CHECKING:
    import argparse
    from collections.abc import Sequence

    from watchdog.observers.api import BaseObserver

args_handling_logger: logging.Logger = logging.getLogger(__name__)


def _add_to_startup(
    *,
    argv: Sequence[str] | None = None,
    startup_folder: Path | None = None,
) -> None:
    """Add the ran command to startup by creating a vbs file in the 'Startup' folder."""
    if platform.system() != "Windows":  # pragma: win32 no cover
        args_handling_logger.warning(
            "Adding 'auto-file-sorter' to startup is only supported on Windows.",
        )
    else:  # pragma: win32 cover
        if not argv:  # pragma: no cover
            argv = sys.argv

        if startup_folder is None:  # pragma: no cover
            startup_folder = Path(os.path.expandvars("%APPDATA%")).joinpath(
                "Microsoft",
                "Windows",
                "Start Menu",
                "Programs",
                "Startup",
            )

        args_handling_logger.debug("argv=%s", argv)

        flag_patterns_to_be_removed: re.Pattern[str] = re.compile(
            r"-v+|--verbose|--autostart",
        )

        cleaned_argv: list[str] = [
            arg for arg in argv if flag_patterns_to_be_removed.fullmatch(arg) is None
        ]
        args_handling_logger.debug(
            "Removed verbosity and autostart flags: '%s'",
            cleaned_argv,
        )
        cmd: str = " ".join(cleaned_argv)
        args_handling_logger.debug("Adding '%s' to autostart", cmd)

        args_handling_logger.debug("Startup folder location: '%s'", startup_folder)
        path_to_vbs: Path = startup_folder / "auto-file-sorter.vbs"

        args_handling_logger.debug("Writing to vsb file: '%s'", path_to_vbs)
        try:
            path_to_vbs.write_text(
                'Set objShell = WScript.CreateObject("WScript.Shell")'
                f'\nobjShell.Run "{cmd}", 0, True\n',
                encoding="utf-8",
            )
            args_handling_logger.info(
                "Added '%s' with '%s' to startup",
                path_to_vbs,
                cmd,
            )
        except PermissionError:
            args_handling_logger.critical(
                "Permission denied to open and read from '%s'",
                path_to_vbs,
            )
        except FileNotFoundError:  # pragma: no cover
            args_handling_logger.critical(
                "Unable to find '%s'",
                path_to_vbs,
            )
        except OSError:
            args_handling_logger.critical(
                "I/O-related error occurred while opening and reading from '%s'",
                path_to_vbs,
            )


def resolved_path_from_str(path_as_str: str) -> Path:
    """Return the absolute path given a string of a path."""
    return Path(path_as_str.strip()).resolve()


def handle_write_args(args: argparse.Namespace) -> int:
    """Handle the ``write`` subcommand."""
    args_handling_logger.debug("Reading from configs")
    configs: dict[str, str] = read_from_configs(configs=args.configs_location)

    if args.new_config is not None:
        args_handling_logger.debug("args.new_config=%s", repr(args.new_config))

        new_extension, new_path = (
            args.new_config[0].lower().replace(" ", ""),
            args.new_config[1].strip(),
        )
        args_handling_logger.debug(
            "Normalized '%s' to '%s'",
            args.new_config[0],
            new_extension,
        )
        args_handling_logger.debug(
            "Normalized '%s' to '%s'",
            args.new_config[1],
            new_path,
        )

        if not new_extension or not new_path:
            args_handling_logger.critical(
                "Either an empty extension '%s' or an empty path '%s' was specified to add, "
                "which is invalid",
                new_extension,
                new_path,
            )
            return EXIT_FAILURE

        if FILE_EXTENSION_PATTERN.fullmatch(new_extension) is None:
            args_handling_logger.critical(
                "Given extension '%s' is invalid",
                new_extension,
            )
            return EXIT_FAILURE

        args_handling_logger.debug("Got '%s': '%s'", new_extension, new_path)

        configs[new_extension] = new_path
        args_handling_logger.log(
            CONFIG_LOG_LEVEL,
            "Updated '%s': '%s' from '%s'",
            new_extension,
            new_path,
            args.configs_location,
        )

    if args.json_file is not None:
        args_handling_logger.debug(
            "args.json_file='%s'",
            repr(args.json_file),
        )

        if args.json_file.suffix.lower() != ".json":
            args_handling_logger.critical(
                "Configs can only be read from json files",
            )
            return EXIT_FAILURE

        args_handling_logger.debug("Reading from '%s'", args.json_file)
        try:
            new_configs_from_json: dict[str, str] = json.loads(
                args.json_file.read_text(encoding="utf-8"),
            )
        except FileNotFoundError:
            args_handling_logger.critical(
                "Unable to find '%s'",
                args.json_file,
            )
            return EXIT_FAILURE
        except PermissionError:
            args_handling_logger.critical(
                "Permission denied to open and read from '%s'",
                args.json_file,
            )
            return EXIT_FAILURE
        except OSError:
            args_handling_logger.critical(
                "Operating system-related error occurred while opening and reading from '%s'",
                args.json_file,
            )
            return EXIT_FAILURE
        except json.JSONDecodeError:
            args_handling_logger.critical(
                "Given JSON file is not correctly formatted: '%s'",
                args.json_file,
            )
            return EXIT_FAILURE
        args_handling_logger.debug("Read from '%s'", args.json_file)

        configs.update(new_configs_from_json)
        args_handling_logger.log(
            CONFIG_LOG_LEVEL,
            "Loaded '%s' into configs",
            args.json_file,
        )

    if args.configs_to_be_removed is not None:
        args_handling_logger.debug(
            "args.configs_to_be_removed=%s",
            repr(args.configs_to_be_removed),
        )

        for config in args.configs_to_be_removed:
            extension: str = config.replace(" ", "").lower()
            args_handling_logger.debug("Stripped '%s' to '%s'", config, extension)

            if FILE_EXTENSION_PATTERN.fullmatch(extension) is None:
                args_handling_logger.warning(
                    "Skipping invalid extension: '%s'",
                    extension,
                )
                continue

            args_handling_logger.debug("Normalized '%s' to '%s'", config, extension)

            args_handling_logger.debug("Removing '%s'", extension)
            try:
                del configs[extension]
            except KeyError:
                args_handling_logger.warning(
                    "Ignoring '%s', because it is not in the configs",
                    extension,
                )
                continue
            args_handling_logger.log(
                CONFIG_LOG_LEVEL,
                "Removed '%s'",
                extension,
            )
    write_to_configs(configs, configs=args.configs_location)
    return EXIT_SUCCESS


def handle_read_args(args: argparse.Namespace) -> int:
    """Handle the ``read`` subcommand."""
    args_handling_logger.debug("Reading from configs")
    configs: dict[str, str] = read_from_configs(configs=args.configs_location)

    if args.get_configs:
        args_handling_logger.debug("args.get_configs=%s", repr(args.get_configs))

        args_handling_logger.debug(
            "Getting selected configs and storing them in dict",
        )

        selected_configs: dict[str, Path] = {}

        for config in args.get_configs:
            extension: str = config.replace(" ", "").lower()

            if FILE_EXTENSION_PATTERN.fullmatch(extension) is None:
                args_handling_logger.warning(
                    "Ignoring invalid extension '%s'",
                    extension,
                )
                continue

            if extension not in configs:
                args_handling_logger.warning(
                    "Ignoring '%s', because it is not in the configs",
                    extension,
                )
                continue

            try:
                selected_configs[extension] = resolved_path_from_str(configs[extension])
            except KeyError:  # pragma: no cover
                args_handling_logger.warning(
                    "Unable to get the respetive path from '%s' "
                    "of one of the given extensions '%s'",
                    args.configs_location,
                    extension,
                )
                continue

        if not selected_configs:
            args_handling_logger.critical("No valid extensions selected")
            args_handling_logger.debug(
                "repr(selected_configs)=%s",
                repr(selected_configs),
            )
            return EXIT_FAILURE

        args_handling_logger.debug("Printing from %s", selected_configs)
        for extension, path in selected_configs.items():
            print(f"{extension}: {path}")
        args_handling_logger.log(
            CONFIG_LOG_LEVEL,
            "Printed the selected configs",
        )
    else:
        for extension, path_as_str in configs.items():
            print(f"{extension}: {resolved_path_from_str(path_as_str)}")
        args_handling_logger.log(
            CONFIG_LOG_LEVEL,
            "Printed all the configs",
        )
    return EXIT_SUCCESS


def handle_track_args(args: argparse.Namespace) -> int:
    """Handle the ``track`` subcommand."""
    tracked_paths: list[Path] = args.tracked_paths
    args_handling_logger.debug("tracked_paths=%s", tracked_paths)

    args_handling_logger.debug("Reading from configs")
    configs: dict[str, str] = read_from_configs(configs=args.configs_location)

    if not configs:
        args_handling_logger.critical(
            "No paths for extensions defined in '%s'",
            args.configs_location,
        )
        return EXIT_FAILURE

    args_handling_logger.debug("Resolving extension paths")
    extension_paths: dict[str, Path] = {
        extension: resolved_path_from_str(path_as_str)
        for extension, path_as_str in configs.items()
    }
    args_handling_logger.info("Got extension paths")

    observers: list[BaseObserver] = []
    for path in tracked_paths:
        if not path.exists():
            args_handling_logger.warning(
                "Skipping '%s', because it does not exist",
                path,
            )
            continue

        if path.is_file():
            args_handling_logger.warning(
                "Skipping '%s', expected a directory, not a file",
                path,
            )
            continue

        args_handling_logger.debug(
            "Creating FileModifiedEventHandler instance tracking '%s'",
            path,
        )
        event_handler: OnModifiedEventHandler = OnModifiedEventHandler(
            path,
            extension_paths,
            args.path_for_undefined_extensions,
        )

        args_handling_logger.debug("Creating observer")
        observer: BaseObserver = Observer()
        args_handling_logger.debug("Scheduling observer: %s", observer)
        observer.schedule(event_handler, path, recursive=True)
        args_handling_logger.debug("Starting observer: %s", observer)
        observer.start()
        args_handling_logger.info("Started observer: '%s'", observer.name)
        observers.append(observer)
        args_handling_logger.debug("Appended '%s' to %s", observer, observers)

    if not observers:
        args_handling_logger.critical(
            "All given paths are invalid: %s",
            ", ".join(str(path) for path in tracked_paths),
        )
        return EXIT_FAILURE

    args_handling_logger.debug("observers=%s", observers)

    if args.enable_autostart:
        _add_to_startup()

    try:
        while True:
            sleep(60)
    except KeyboardInterrupt:
        args_handling_logger.debug("User stopped/interrupted program")
    finally:
        for observer in observers:
            if observer.is_alive():
                observer.stop()
                args_handling_logger.info("Stopped observer: %s", observer.name)
            observer.join()
            args_handling_logger.debug("Joined observer: %s", observer)
    return EXIT_SUCCESS


def handle_locations_args(args: argparse.Namespace) -> int:
    """Handle the ``locations`` subcommand."""
    if args.get_log_location:
        print(args.log_location)

    if args.get_configs_location:
        print(args.configs_location)

    return EXIT_SUCCESS
