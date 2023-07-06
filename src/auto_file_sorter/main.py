#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Main module."""
from __future__ import annotations

__all__: list[str] = ["main"]

import argparse
import logging
from typing import Final, Optional, Sequence, TextIO

from auto_file_sorter import __status__, __version__
from auto_file_sorter.args_handling import (
    handle_locations_args,
    handle_read_args,
    handle_track_args,
    handle_write_args,
    resolved_path_from_str,
)
from auto_file_sorter.constants import (
    CONFIG_LOG_LEVEL,
    DEFAULT_LOG_LOCATION,
    LOG_FORMAT,
    MAX_VERBOSITY_LEVEL,
    MOVE_LOG_LEVEL,
    STREAM_HANDLER_FORMATTER,
)

_MAIN_LOGGER: Final[logging.Logger] = logging.getLogger(__name__)

_VERBOSE_OUTPUT_LEVELS: Final[dict[int, int]] = {
    1: logging.WARNING,
    2: logging.INFO,
    3: logging.DEBUG,
}


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Runs the program."""
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="auto-file-sorter",
        description="Automatically sorts files in a directory based on their extension.",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__} {__status__}",
        help="Show version of auto-file-sorter",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        dest="debugging",
        help="Enable debugging by setting logging level to DEBUG",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        dest="verbosity_level",
        default=0,
        help="Increase output verbosity (up to 3 levels; third requires debugging)",
    )
    parser.add_argument(
        "--log-location",
        dest="log_location",
        default=DEFAULT_LOG_LOCATION,
        type=resolved_path_from_str,
        metavar="LOCATION",
        help="Specify custom location for the log file (default: location of the program)",
    )

    subparsers: argparse._SubParsersAction[  # noqa: SLF001 # type: ignore
        argparse.ArgumentParser
    ] = parser.add_subparsers(
        title="subcommands",
        description="Track a directory, configure the extension paths"
        "or get the locations of the log and config file",
        required=True,
    )

    # "track" subcommand
    track_parser: argparse.ArgumentParser = subparsers.add_parser(
        "track",
        help="Track a directory",
    )
    track_parser.set_defaults(handle=handle_track_args)
    track_parser.add_argument(
        dest="tracked_paths",
        type=resolved_path_from_str,
        nargs="+",
        metavar="PATHS",
        help="Paths to the directories to be tracked",
    )
    track_parser.add_argument(
        "--autostart",
        action="store_true",
        dest="enable_autostart",
        help="Add the current command to run on startup (only works on windows)",
    )

    # "write" subcommand
    write_parser: argparse.ArgumentParser = subparsers.add_parser(
        "write",
        help="Write to the configs",
    )
    write_parser.set_defaults(handle=handle_write_args)
    write_parser.add_argument(
        "-a",
        "--add",
        dest="new_config",
        type=str,
        nargs=2,
        metavar="CONFIG",
        help="Add path for extension",
    )
    write_parser.add_argument(
        "-r",
        "--remove",
        dest="configs_to_be_removed",
        type=str,
        nargs="+",
        metavar="CONFIG",
        help="Remove extension(s) and its/their path from 'configs.json'",
    )
    write_parser.add_argument(
        "-j",
        "--json",
        dest="json_file",
        type=resolved_path_from_str,
        nargs="+",
        metavar="PATH",
        help="Load new configs from a json file into 'configs.json'",
    )

    # "read" subcommand
    read_parser: argparse.ArgumentParser = subparsers.add_parser(
        "read",
        help="Read from the configs",
    )
    read_parser.set_defaults(handle=handle_read_args)
    read_parser.add_argument(
        dest="get_configs",
        type=str,
        nargs="*",
        default=[],
        metavar="CONFIGS",
        help="Get the extensions and their path from 'configs.json' (default: all configs)",
    )

    # "locations" subcommand
    locations_parser: argparse.ArgumentParser = subparsers.add_parser(
        "locations",
        help="Output the locations of the log and configs file",
    )
    locations_parser.set_defaults(handle=handle_locations_args)
    locations_parser.add_argument(
        "-l",
        "--log",
        action="store_true",
        dest="get_log_location",
        help="Get the location of the log file",
    )
    locations_parser.add_argument(
        "-c",
        "--config",
        action="store_true",
        dest="get_config_location",
        help="Get the location of the config file",
    )

    args: argparse.Namespace = parser.parse_args(argv)

    # Define custom "MOVE" and "CONFIG" logging level >= logging.CRITICAL (50)
    # so it can be handeled by the stream handler if verbose logging is enabled
    logging.addLevelName(MOVE_LOG_LEVEL, "MOVE")
    logging.addLevelName(CONFIG_LOG_LEVEL, "CONFIG")

    file_handler: logging.FileHandler = logging.FileHandler(
        filename=args.log_location,
        mode="w",
        encoding="utf-8",
    )

    handlers: list[logging.Handler] = [file_handler]

    if args.verbosity_level:
        stream_handler: logging.StreamHandler[TextIO] = logging.StreamHandler()
        stream_handler.setFormatter(STREAM_HANDLER_FORMATTER)
        if args.verbosity_level > MAX_VERBOSITY_LEVEL:
            stream_handler.setLevel(MAX_VERBOSITY_LEVEL)
        else:
            stream_handler.setLevel(_VERBOSE_OUTPUT_LEVELS[args.verbosity_level])
        handlers.append(stream_handler)

    log_level: int = logging.INFO if not args.debugging else logging.DEBUG

    logging.basicConfig(
        level=log_level,
        format=LOG_FORMAT,
        handlers=handlers,
    )

    if args.verbosity_level > MAX_VERBOSITY_LEVEL:
        _MAIN_LOGGER.warning(
            "Maximum verbosity level exceeded. Using maximum level of 3.",
        )

    if args.verbosity_level >= MAX_VERBOSITY_LEVEL and not args.debugging:
        _MAIN_LOGGER.warning(
            "Using maximum verbosity level, but debugging is disabled. "
            "To get the full output add the '-d' flag to enable debugging",
        )

    _MAIN_LOGGER.info(
        "Started logging at '%s' with level %s",
        args.log_location,
        log_level,
    )

    _MAIN_LOGGER.debug("args=%s", repr(args))

    exit_code: int = args.handle(args)

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
