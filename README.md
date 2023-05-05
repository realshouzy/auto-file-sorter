# File Sorter

[![Code Size](https://img.shields.io/github/languages/code-size/realshouzy/file-sorter)](https://github.com/realshouzy/file-sorter)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# !!! This README is outdated, it will be updated soon

This is a python automation that watches a folder and sorts the files into their respective folders.

## Installation

Make sure you have python (^3.11) installed, and then install all the required libraries by typing the following command in the root of the project:

```bash
pip install -r requierments.txt
```

The used packages are:

```python
# standard library
import json
import sys
import contextlib
import typing
import datetime
import logging
import shutil

# third party
import PySimpleGUI
import watchdog
```

### macOS Installation

Add the following command to the ``Automator`` app. You can find a tutorial [here](https://youtu.be/LfxZMofHs_U?t=658).

```bash
python3 /path/to/the/script/main.py
```

and add any needed extensions and configurations to the [settings.json file](/scripts/settings.json). Finally restart your computer.

## Windows Installation

Create a ``.bat`` file in ``C:\Users\{user here}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup`` with the following content:

```bash
start /b python C:\path\to\the\script}\main.py
```

and add any needed extensions and configurations to the [settings.json file](/scripts/settings.json). Finally restart your computer.

Perhabs I'll add an executable in the future.

## Usage

Throw stuff into the tracked folder and it will be automatically sorted for you.
