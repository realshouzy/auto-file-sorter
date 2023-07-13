# auto-file-sorter

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/realshouzy/auto-file-sorter/main.svg)](https://results.pre-commit.ci/latest/github/realshouzy/auto-file-sorter/main)
[![Code Size](https://img.shields.io/github/languages/code-size/realshouzy/auto-file-sorter)](https://github.com/realshouzy/auto-file-sorter)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%20|%203.9%20|%203.10%20|%203.11-blue.svg)](https://www.python.org/downloads)
[![GitHub top language](https://img.shields.io/github/languages/top/realshouzy/auto-file-sorter)](https://www.python.org)
[![Contributors](https://img.shields.io/github/contributors/realshouzy/auto-file-sorter)](https://github.com/realshouzy/auto-file-sorter/graphs/contributors)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/realshouzy/auto-file-sorter/blob/main/LICENSE)

**``auto-file-sorter`` is a Python automation tool that tracks a directory and sorts files into their respective folders based on their file extensions.**

## Installation

Make sure you have Python 3.8 or later installed. You can install the package using ``pip``:

```bash
pip install git+https://github.com/realshouzy/auto-file-sorter.git
```

Alternatively, you can clone the repository and install the required dependencies by executing the following commands in the root of the project:

```bash
git clone https://github.com/realshouzy/auto-file-sorter.git
pip install -r requierments.txt
```

The project uses the following packages and libraries:

```python
# standard library
import argparse
import concurrent.futures
import datetime
import json
import logging
import os
import pathlib
import platform
import re
import shutil
import sys
import time
import typing

# third party
# import watchdog
import watchdog.events
import watchdog.observers

# only for type annotations; not used at runtime
import watchdog.observers.api
```

## Documentation

Consult ``auto-file-sorter --help`` / ``auto-file-sorter -h`` for the full set of options. This also applies to all subcommands:

- ``auto-file-sorter track``
- ``auto-file-sorter read``
- ``auto-file-sorter write``
- ``auto-file-sorter locations``

### Arguments and flags of ``auto-file-sorter``

| Argument and flags | Use |
| -------- | ------- |
| ``--version`` / ``-V`` | Outputs the installed version and status, either ``production`` or ``development``.                                                                                                                                                                                                                             |
| ``--debug`` / ``-d``   | Sets the logging level to 10 (debugging), enabling more informative debugging logs.                                                                                                                                                                                                                             |
| ``--verbose`` / ``-v`` | Enables verbose outputs. It can be used up to three levels, with each level printing more logs to the stream. The first level prints all logs up to the logging level WARNING, the second level prints all logs up to INFO, and the third level prints all logs up to DEBUG (this requires the debugging flag). |
| ``--log-location``     | Specifies the path to a log file. By default, the log file will be located with the source code.                                                                                                                                                                                                                |

### Arguments and flags of ``auto-file-sorter track``

| Argument and flags | Use |
| -------- | ------- |
| Positional arguments | Paths to the directories to be tracked. At least one directory path must be provided. The tool will track all the given directories simultaneously using threading. |
| ``--undefined-extensions`` / ``-u`` | Path in which files whose extensions are not defined in the configs will be moved. If no path was specified, said files will be skipped. |
| ``--autostart`` (only supported on Windows) | Runs the command on startup. Refer to [Windows setup](#windows-setup) for more information. |

### Arguments of ``auto-file-sorter read``

| Argument | Use |
| -------- | ------- |
| Positional arguments | Extensions for which their respective paths should be read from the configs.json file. If no extensions are given, it will print out the entire ``configs.json`` file. |

### Arguments of ``auto-file-sorter write``

| Argument | Use |
| -------- | ------- |
| ``--add`` / ``-a`` | Adds an extension and its corresponding path to the ``configs.json`` file. It takes two arguments: the extension and the path to which files with this extension will be saved. If the extension already exists, the path will be overridden. |
| ``--remove`` / ``-r`` | Removes one or more extensions and their respective paths from the configuration. |
| ``--json`` / ``-j`` | Loads one or more ``json`` files that bind extensions to paths and merges them into the ``configs.json`` file. |

The json files should be structured similarly to the ``configs.json`` file. An example (with Windows paths) can be found in [``example_configs.json``](/example_configs.json).
Ultimately you can directly modify the ``configs.json`` file yourself.

### Flags of ``auto-file-sorter locations``

| Argument | Use |
| -------- | ------- |
| ``--log`` / ``-l`` | Prints the location of the log file |
| ``--config`` / ``-c`` | Prints the location of the config file |

## Run on startup

### Windows setup

To run the tool on startup, add the ``--autostart`` flag after the ``track`` subcommand. This will add the command to the Startup folder as a ``.vbs`` file, ensuring it runs in the background.

To avoid the overhead of creating a StreamHandler and prevent overwriting the ``.vbs`` file on every startup, it removes all occurrences of ``--verbose`` / ``-v`` as well as ``--autostart``.

An example of this transformation:

| Before | After |
| -------- | ------- |
| ``auto-file-sorter -d -vvv track C:\path\to\be\tracked`` | ``C:\path\to\auto-file-sorter.exe -d track C:\path\to\be\tracked`` |

This will then be run by the ``.vbs`` file on startup:

```vbs
Set objShell = WScript.CreateObject("WScript.Shell")
objShell.Run "C:\path\to\auto-file-sorter.exe -d track C:\path\to\be\tracked", 0, True
```

### macOS setup

Add the desired command to the ``Automator`` app. You can find a tutorial [here](https://youtu.be/LfxZMofHs_U?t=658).

### Linux setup

Due to the wide variety of Linux distributions and their differences, it is up to the user to configure ``auto-file-sorter`` to run on startup.

## Usage

Simply place files into the tracked folder, and the tool will automatically sort them for you.

## Excpetion handling

Most exceptions will be logged in a log file. If an exception should occur, the program will handly gracefuly by exiting with exit code 1, except in cases where an exception is encountered while moving a file. This is due to threading and ensures that everything gets properly garbage collected. This behavior is specifically implemented to address threading concerns and ensure proper garbage collection. In such cases, the respective thread will exit, while the main program continues its execution. Ultimately, the user has the option to stop the program manually. This approach allows for proper cleanup and termination of resources.

## Regarding the lack of tests

While this project currently lacks tests, I acknowledge the importance of testing for ensuring code quality and reliability is. Initially, due to my limited knowledge when starting the project, I didn't prioritize writing tests. As the project evolved, I didn't care to invest time in writing tests, as I originally intended it to be a smaller-scale project. Recognizing the significance of testing in continuous integration, I have taken the initiative to write tests. I have created a dedicated [branch](https://github.com/realshouzy/auto-file-sorter/tree/add-tests), where you can find all the essential information.

## Contributing

If you are interested in contributing to this project, please find more information [here](/CONTRIBUTING.md).

## License

[MIT](/LICENSE)

## Credits

This project was originally inspired by Kalle Hallden's [desktop_cleaner](https://github.com/KalleHallden/desktop_cleaner) project.
