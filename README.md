# File Sorter

This is a python automation that watches a folder and sorts the files into their respective folders.

## Installation

Make sure you have python (^3.11) installed, and then install all the required libraries by typing the following command on the root of the project:

```bash
pip install -r requierments.txt
```

### macOS Installation

Add the following command to the ``Automator`` app. You can find a tutorial [here](https://youtu.be/LfxZMofHs_U?t=658).

```bash
python /path/to/the/script/main.py
```

and add any needed extensions and configurations to the [settings.json list](../scripts/settings.json). Finally restart your computer.

## Windows Installation

Create a ``.bat`` file in ``C://Users/{user here}/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup`` with the following content:

```bash
start /b python C://path/to/the/script/main.py
```

and add any needed extensions and configurations to the [settings.json list](../scripts/settings.json). Finally restart your computer.

## Usage

Throw stuff into the tracked folder, and it will be automatically sorted for you.
