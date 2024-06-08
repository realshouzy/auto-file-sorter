"""Module responsible for handling the args."""

from __future__ import annotations

__all__: list[str] = [
    "handle_write_args",
    "handle_read_args",
    "handle_track_args",
    "handle_locations_args",
]

import logging
import os.path
import platform
import re
import sys
from pathlib import Path
from time import sleep
from typing import TYPE_CHECKING

from watchdog.observers import Observer

from auto_file_sorter.configs_handling import (
    add_new_config_to_configs,
    get_extension_paths_from_configs,
    get_selected_configs,
    load_json_file_into_configs,
    read_from_configs,
    remove_configs,
    write_to_configs,
)
from auto_file_sorter.constants import CONFIG_LOG_LEVEL, EXIT_FAILURE, EXIT_SUCCESS
from auto_file_sorter.event_handling import OnCreatedEventHandler
from auto_file_sorter.utils import resolved_path_from_str

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


def handle_write_args(args: argparse.Namespace) -> int:
    """Handle the ``write`` subcommand."""
    exit_code: int = EXIT_SUCCESS

    args_handling_logger.debug("Reading from configs")
    configs: dict[str, str] = read_from_configs(configs=args.configs_location)

    if args.new_config is not None:
        exit_code |= add_new_config_to_configs(args.new_config, configs)

    if args.json_file is not None:
        exit_code |= load_json_file_into_configs(args.json_file, configs)

    if args.configs_to_be_removed is not None:
        exit_code |= remove_configs(args.configs_to_be_removed, configs)

    write_to_configs(configs, configs=args.configs_location)
    return exit_code


def handle_read_args(args: argparse.Namespace) -> int:
    """Handle the ``read`` subcommand."""
    args_handling_logger.debug("Reading from configs")
    configs: dict[str, str] = read_from_configs(configs=args.configs_location)

    if args.get_configs:
        args_handling_logger.debug("args.get_configs=%s", repr(args.get_configs))

        args_handling_logger.debug(
            "Getting selected configs and storing them in dict",
        )

        selected_configs: dict[str, Path] = get_selected_configs(
            args.get_configs,
            configs,
        )

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


def _create_observers(
    tracked_paths: list[Path],
    extension_paths: dict[str, Path],
    path_for_undefined_extensions: Path,
) -> list[BaseObserver]:
    """Create the observers and return them in a list."""
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
        event_handler: OnCreatedEventHandler = OnCreatedEventHandler(
            path,
            extension_paths,
            path_for_undefined_extensions,
        )

        args_handling_logger.debug("Creating observer")
        observer: BaseObserver = Observer()
        observer.name = str(path)
        args_handling_logger.debug("Scheduling observer: %s", observer)
        observer.schedule(event_handler, path, recursive=True)
        observers.append(observer)
        args_handling_logger.debug("Appended '%s' to %s", observer, observers)
    return observers


def _run_observers(observers: list[BaseObserver]) -> int:  # pragma: no cover
    """Start and run the given observers."""
    for observer in observers:
        args_handling_logger.debug("Starting observer: %s", observer)
        observer.start()
        args_handling_logger.info("Started observer: '%s'", observer.name)

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


def handle_track_args(args: argparse.Namespace) -> int:
    """Handle the ``track`` subcommand."""
    args_handling_logger.debug("args.tracked_paths=%s", args.tracked_paths)

    args_handling_logger.debug("Reading from configs")
    configs: dict[str, str] = read_from_configs(configs=args.configs_location)

    if not configs:
        args_handling_logger.critical(
            "No paths for extensions defined in '%s'",
            args.configs_location,
        )
        return EXIT_FAILURE

    extension_paths: dict[str, Path] = get_extension_paths_from_configs(configs)

    observers: list[BaseObserver] = _create_observers(
        args.tracked_paths,
        extension_paths,
        args.path_for_undefined_extensions,
    )

    exit_code: int
    if not observers:
        args_handling_logger.critical(
            "All given paths are invalid: %s",
            ", ".join(str(path) for path in args.tracked_paths),
        )
        exit_code = EXIT_FAILURE
    else:  # pragma: no cover
        args_handling_logger.debug("observers=%s", observers)

        if args.enable_autostart:
            _add_to_startup()

        exit_code = _run_observers(observers)
    return exit_code


def handle_locations_args(args: argparse.Namespace) -> int:
    """Handle the ``locations`` subcommand."""
    if args.get_log_location:
        print(args.log_location)

    if args.get_configs_location:
        print(args.configs_location)

    return EXIT_SUCCESS
