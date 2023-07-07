#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
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
import os
import platform
import re
import sys
from pathlib import Path
from time import sleep
from typing import TYPE_CHECKING, Final

from watchdog.observers import Observer

from auto_file_sorter.configs_handling import read_from_configs, write_to_configs
from auto_file_sorter.constants import (
    CONFIG_LOG_LEVEL,
    CONFIGS_LOCATION,
    EXIT_FAILURE,
    EXIT_SUCCESS,
)
from auto_file_sorter.event_handling import OnModifiedEventHandler

if TYPE_CHECKING:
    import argparse

    from watchdog.observers.api import BaseObserver

_ARGS_HANDLING_LOGGER: Final[logging.Logger] = logging.getLogger(__name__)

_FILE_EXTENSION_PATTERN: Final[re.Pattern[str]] = re.compile(r"^\.[a-zA-Z0-9]+$")


def _add_to_startup() -> None:
    """Add the ran command to startup by creating a vbs file in the 'Startup' folder."""
    if platform.system() != "Windows":
        _ARGS_HANDLING_LOGGER.warning(
            "Adding 'auto-file-sorter' to startup is only supported on Windows.",
        )
        return

    _ARGS_HANDLING_LOGGER.debug("sys.argv=%s", sys.argv)

    flag_patterns_to_be_removed: re.Pattern[str] = re.compile(
        r"-v+|--verbose|--autostart",
    )

    cleaned_sys_argv: list[str] = [
        arg for arg in sys.argv if flag_patterns_to_be_removed.fullmatch(arg) is None
    ]
    _ARGS_HANDLING_LOGGER.debug(
        "Removed verbosity and autostart flags: '%s'",
        cleaned_sys_argv,
    )
    cmd: str = " ".join(cleaned_sys_argv)
    _ARGS_HANDLING_LOGGER.debug("Adding '%s' to autostart", cmd)

    startup_folder: Path = Path(os.path.expandvars("%APPDATA%")).joinpath(
        "Microsoft",
        "Windows",
        "Start Menu",
        "Programs",
        "Startup",
    )
    _ARGS_HANDLING_LOGGER.debug("Startup folder location: '%s'", startup_folder)
    path_to_vbs: Path = startup_folder.joinpath("auto-file-sorter.vbs")

    _ARGS_HANDLING_LOGGER.debug("Opening vbs file: '%s'", path_to_vbs)
    try:
        with open(path_to_vbs, "w", encoding="utf-8") as vbs_file:
            _ARGS_HANDLING_LOGGER.debug("Writing to vsb file: '%s'", vbs_file)
            vbs_file.write(
                'Set objShell = WScript.CreateObject("WScript.Shell")\n'
                f'objShell.Run "{cmd}", 0, True',
            )
    except PermissionError:
        _ARGS_HANDLING_LOGGER.critical(
            "Permission denied to open and read from '%s'",
            path_to_vbs,
        )
        return
    except FileNotFoundError:
        _ARGS_HANDLING_LOGGER.critical(
            "Unable to find '%s'",
            path_to_vbs,
        )
        return
    except OSError:
        _ARGS_HANDLING_LOGGER.critical(
            "I/O-related error occurred while opening and reading from '%s'",
            path_to_vbs,
        )
        return
    _ARGS_HANDLING_LOGGER.info(
        "Added '%s' with '%s' to startup",
        path_to_vbs,
        cmd,
    )


def resolved_path_from_str(path_as_str: str) -> Path:
    """Returns the absolute path given a string of a path."""
    return Path(path_as_str.strip()).resolve()


def handle_write_args(args: argparse.Namespace) -> int:  # noqa: PLR0915
    """Function handling the ``write`` subcommand."""
    _ARGS_HANDLING_LOGGER.debug("Reading from configs")
    configs: dict[str, str] = read_from_configs()

    if args.new_config is not None:
        _ARGS_HANDLING_LOGGER.debug("args.new_config=%s", repr(args.new_config))

        new_extension, new_path = (
            args.new_config[0].lower().replace(" ", ""),
            args.new_config[1].strip(),
        )
        _ARGS_HANDLING_LOGGER.debug(
            "Normalized '%s' to '%s'",
            args.new_config[0],
            new_extension,
        )
        _ARGS_HANDLING_LOGGER.debug(
            "Normalized '%s' to '%s'",
            args.new_config[1],
            new_path,
        )

        if not new_extension or not new_path:
            _ARGS_HANDLING_LOGGER.critical(
                "Either an empty extension '%s' or an empty path '%s' was specified to add, "
                "which is invalid",
                new_extension,
                new_path,
            )
            return EXIT_FAILURE

        if _FILE_EXTENSION_PATTERN.fullmatch(new_extension) is None:
            _ARGS_HANDLING_LOGGER.critical(
                "Given extension '%s' is invalid",
                new_extension,
            )
            return EXIT_FAILURE

        _ARGS_HANDLING_LOGGER.debug("Got '%s': '%s'", new_extension, new_path)

        configs[new_extension] = new_path
        _ARGS_HANDLING_LOGGER.log(
            CONFIG_LOG_LEVEL,
            "Updated '%s': '%s' from %s",
            new_extension,
            new_path,
            CONFIGS_LOCATION,
        )

    if args.json_file is not None:
        _ARGS_HANDLING_LOGGER.debug(
            "args.json_file='%s'",
            repr(args.json_file),
        )

        if args.json_file.suffix.lower() != ".json":
            _ARGS_HANDLING_LOGGER.critical(
                "Configs can only be read from json files",
            )
            return EXIT_FAILURE

        _ARGS_HANDLING_LOGGER.debug("Opening '%s'", args.json_file)
        try:
            with open(args.json_file, "r", encoding="utf-8") as json_file:
                _ARGS_HANDLING_LOGGER.debug(
                    "Reading from '%s'",
                    args.json_file,
                )
                new_configs_from_json: dict[str, str] = json.load(json_file)
        except FileNotFoundError:
            _ARGS_HANDLING_LOGGER.critical(
                "Unable to find '%s'",
                args.json_file,
            )
            return EXIT_FAILURE
        except PermissionError:
            _ARGS_HANDLING_LOGGER.critical(
                "Permission denied to open and read from '%s'",
                args.json_file,
            )
            return EXIT_FAILURE
        except OSError:
            _ARGS_HANDLING_LOGGER.critical(
                "Operating system-related error occurred while opening and reading from '%s'",
                args.json_file,
            )
            return EXIT_FAILURE
        except json.JSONDecodeError:
            _ARGS_HANDLING_LOGGER.critical(
                "Given JSON file is not correctly formatted: %s",
                args.json_file,
            )
            return EXIT_FAILURE
        _ARGS_HANDLING_LOGGER.debug("Read from '%s'", args.json_file)

        configs |= new_configs_from_json
        _ARGS_HANDLING_LOGGER.log(
            CONFIG_LOG_LEVEL,
            "Loaded '%s' into configs",
            args.json_file,
        )

    if args.configs_to_be_removed is not None:
        _ARGS_HANDLING_LOGGER.debug(
            "args.configs_to_be_removed=%s",
            repr(args.configs_to_be_removed),
        )

        for config in args.configs_to_be_removed:
            extension: str = config.replace(" ", "").lower()
            _ARGS_HANDLING_LOGGER.debug("Stripped '%s' to '%s'", config, extension)

            if _FILE_EXTENSION_PATTERN.fullmatch(extension) is None:
                _ARGS_HANDLING_LOGGER.warning(
                    "Skipping invalid extension: '%s'",
                    extension,
                )
                continue

            _ARGS_HANDLING_LOGGER.debug("Normalized '%s' to '%s'", config, extension)

            _ARGS_HANDLING_LOGGER.debug("Removing '%s'", extension)
            try:
                del configs[extension]
            except KeyError:
                _ARGS_HANDLING_LOGGER.warning(
                    "Ignoring '%s', because it is not in the configs",
                    extension,
                )
                continue
            _ARGS_HANDLING_LOGGER.log(
                CONFIG_LOG_LEVEL,
                "Removed '%s'",
                extension,
            )
    write_to_configs(configs)
    return EXIT_SUCCESS


def handle_read_args(args: argparse.Namespace) -> int:
    """Function handling the ``read`` subcommand."""
    _ARGS_HANDLING_LOGGER.debug("Reading from configs")
    configs: dict[str, str] = read_from_configs()

    if args.get_configs:
        _ARGS_HANDLING_LOGGER.debug("args.get_configs=%s", repr(args.get_configs))

        _ARGS_HANDLING_LOGGER.debug(
            "Getting selected configs and storing them in dict",
        )

        selected_configs: dict[str, Path] = {}

        for config in args.get_configs:
            extension: str = config.replace(" ", "").lower()

            if _FILE_EXTENSION_PATTERN.fullmatch(extension) is None:
                _ARGS_HANDLING_LOGGER.warning(
                    "Ignoring invalid extension '%s'",
                    extension,
                )
                continue

            if extension not in configs:
                _ARGS_HANDLING_LOGGER.warning(
                    "Ignoring '%s', because it is not in the configs",
                    extension,
                )
                continue

            try:
                selected_configs[extension] = resolved_path_from_str(configs[extension])
            except KeyError:
                _ARGS_HANDLING_LOGGER.warning(
                    "Unable to get the respetive path from '%s' "
                    "of one of the given extensions '%s'",
                    CONFIGS_LOCATION,
                    extension,
                )
                continue

        _ARGS_HANDLING_LOGGER.debug("Printing from %s", selected_configs)
        for extension, path in selected_configs.items():
            print(f"{extension}: {path}")
        _ARGS_HANDLING_LOGGER.log(
            CONFIG_LOG_LEVEL,
            "Printed the selected configs",
        )
    else:
        for extension, path_as_str in configs.items():
            print(f"{extension}: {resolved_path_from_str(path_as_str)}")
        _ARGS_HANDLING_LOGGER.log(
            CONFIG_LOG_LEVEL,
            "Printed all the configs",
        )
    return EXIT_SUCCESS


def handle_track_args(args: argparse.Namespace) -> int:
    """Function handling the ``track`` subcommand."""
    if args.enable_autostart:
        _add_to_startup()

    tracked_paths: list[Path] = args.tracked_paths
    _ARGS_HANDLING_LOGGER.debug("tracked_paths=%s", tracked_paths)

    _ARGS_HANDLING_LOGGER.debug("Reading from configs")
    configs: dict[str, str] = read_from_configs()

    if not configs:
        _ARGS_HANDLING_LOGGER.critical(
            "No paths for extensions defined in '%s'",
            CONFIGS_LOCATION,
        )
        return EXIT_FAILURE

    _ARGS_HANDLING_LOGGER.debug("Resolving extension paths")
    extension_paths: dict[str, Path] = {
        extension: resolved_path_from_str(path_as_str)
        for extension, path_as_str in configs.items()
    }
    _ARGS_HANDLING_LOGGER.info("Got extension paths")

    observers: list[BaseObserver] = []
    for path in tracked_paths:
        _ARGS_HANDLING_LOGGER.debug(
            "Creating FileModifiedEventHandler instance tracking '%s'",
            path,
        )
        event_handler: OnModifiedEventHandler = OnModifiedEventHandler(
            path,
            extension_paths,
        )

        _ARGS_HANDLING_LOGGER.debug("Creating observer")
        observer: BaseObserver = Observer()
        _ARGS_HANDLING_LOGGER.debug("Scheduling observer: %s", observer)
        observer.schedule(event_handler, path, recursive=True)
        _ARGS_HANDLING_LOGGER.debug("Starting observer: %s", observer)
        observer.start()
        _ARGS_HANDLING_LOGGER.info("Started observer: '%s'", observer.name)
        observers.append(observer)
        _ARGS_HANDLING_LOGGER.debug("Appended '%s' to %s", observer, observers)

    _ARGS_HANDLING_LOGGER.debug("observers=%s", observers)

    try:
        while True:
            sleep(60)
    except KeyboardInterrupt:
        _ARGS_HANDLING_LOGGER.debug("User stopped/interrupted program")
    finally:
        for observer in observers:
            if observer.is_alive():
                observer.stop()
                _ARGS_HANDLING_LOGGER.info("Stopped observer: %s", observer.name)
            observer.join()
            _ARGS_HANDLING_LOGGER.debug("Joined observer: %s", observer)
    return EXIT_SUCCESS


def handle_locations_args(args: argparse.Namespace) -> int:
    """Function handling the ``locations`` subcommand."""
    if args.get_log_location:
        print(args.log_location)

    if args.get_config_location:
        print(CONFIGS_LOCATION)

    return EXIT_SUCCESS
