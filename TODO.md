# TODO

## Potential features for the future

- [x] Add ~~``autostart`` subcommand~~ ``-A`` / ``--autostart`` option to ``track`` subcommand, which runs the automation on startup
- [x] Add ``-l`` / ``--load`` to ``config`` subcommand to load a list of extension paths from a file (``json`` or ~~``txt``~~)
- [x] Add argument to specify custom location for log file
- [x] Tracking multiple paths simultaneous
- [x] Add option to ``read`` from config (*also ``write``)
- [x] Add option to output the loaction of the log and configs file
- [ ] Add option to specify a location for ~~unknown~~ undefined file extensions; skips them by default (which is already the case)

## Bugs and security issues

- [ ] Fix proper exception handling and cleanup during event handling

## Other

- [x] Adjust ``-A`` / ``--autostart`` so no window opens
- [x] Update README
- [ ] Add ``pre-commit``
