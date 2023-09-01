#!/usr/bin/env python3
"""Main module."""
from __future__ import annotations

__all__: list[str] = ["main"]

import argparse
import logging
from typing import TYPE_CHECKING, TextIO

from auto_file_sorter import __version__
from auto_file_sorter.args_handling import (
    handle_locations_args,
    handle_read_args,
    handle_track_args,
    handle_write_args,
    resolved_path_from_str,
)
from auto_file_sorter.constants import (
    CONFIG_LOG_LEVEL,
    DEFAULT_CONFIGS_LOCATION,
    DEFAULT_LOG_LOCATION,
    LOG_FORMAT,
    MAX_VERBOSITY_LEVEL,
    MOVE_LOG_LEVEL,
    STREAM_HANDLER_FORMATTER,
    VERBOSE_OUTPUT_LEVELS,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

main_logger: logging.Logger = logging.getLogger(__name__)


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse arguments from ``argv``."""
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="auto-file-sorter",
        description="Automatically sorts files in a directory based on their extension.",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
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
        metavar="PATH",
        help="Specify custom location for the log file (default: location of the program)",
    )
    parser.add_argument(
        "--configs-location",
        dest="configs_location",
        default=DEFAULT_CONFIGS_LOCATION,
        type=resolved_path_from_str,
        metavar="PATH",
        help="Specify custom location for the configs file (default: location of the program)",
    )

    subparsers: argparse._SubParsersAction[  # noqa: SLF001
        argparse.ArgumentParser
    ] = parser.add_subparsers(
        title="subcommands",
        description="Track a directory, configure the extension paths"
        "or get the locations of the log and configs file",
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
        "-u",
        "--undefined-extensions",
        dest="path_for_undefined_extensions",
        type=resolved_path_from_str,
        metavar="PATH",
        help="Specify a path for undefined extensions",
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
        help="Remove extension(s) and its/their path from the configs file",
    )
    write_parser.add_argument(
        "-j",
        "--json",
        dest="json_file",
        type=resolved_path_from_str,
        metavar="PATH",
        help="Load new configs from a JSON file into the configs file",
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
        help="Get the extensions and their path from the configs file (default: all configs)",
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
        dest="get_configs_location",
        help="Get the location of the configs file",
    )

    return parser.parse_args(argv)


def _setup_logging(args: argparse.Namespace) -> None:
    """Set up logging based on the provided arguments."""
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
        stream_handler.setLevel(
            VERBOSE_OUTPUT_LEVELS.get(args.verbosity_level, MAX_VERBOSITY_LEVEL),
        )
        handlers.append(stream_handler)

    log_level: int = logging.INFO if not args.debugging else logging.DEBUG

    logging.basicConfig(
        level=log_level,
        format=LOG_FORMAT,
        handlers=handlers,
    )

    if args.verbosity_level > MAX_VERBOSITY_LEVEL:
        main_logger.warning(
            "Maximum verbosity level exceeded. Using maximum level of 3.",
        )

    if args.verbosity_level >= MAX_VERBOSITY_LEVEL and not args.debugging:
        main_logger.warning(
            "Using maximum verbosity level, but debugging is disabled. "
            "To get the full output add the '-d' flag to enable debugging",
        )

    main_logger.info(
        "Started logging at '%s' with level %s",
        args.log_location,
        log_level,
    )


def _check_specified_locations(args: argparse.Namespace) -> None:
    """Check the log and configs locations are their respective files types."""
    if args.log_location.suffix.lower() != ".log":
        main_logger.warning(
            "Given logging location '%s' is not a '.log' file. "
            "Using default location: '%s'",
            args.log_location,
            DEFAULT_LOG_LOCATION,
        )
        args.log_location = DEFAULT_LOG_LOCATION

    if args.configs_location.suffix.lower() != ".json":
        main_logger.warning(
            "Given configs location '%s' is not a '.json' file. "
            "Using default location: '%s'",
            args.configs_location,
            DEFAULT_CONFIGS_LOCATION,
        )
        args.configs_location = DEFAULT_CONFIGS_LOCATION


def main() -> int:  # pragma: no cover
    """Run the program."""
    args: argparse.Namespace = _parse_args()

    _setup_logging(args)

    _check_specified_locations(args)

    main_logger.debug("args=%s", repr(args))

    exit_code: int = args.handle(args)

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
