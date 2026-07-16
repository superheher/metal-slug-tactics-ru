# Contributing

Thanks for your interest! Fixes to the translation and typos are welcome.

## Translation fixes

- The text is in `translation/ru.json`, a flat dictionary `"id": "Russian text"`.
- **Do not touch** the paths in `{...}` or the tags `<...>` — the build checks them and will not
  let a breakage through. The text after the colon in a placeholder (`{Move:перемещает}`) is visible
  to the player — that can be edited.
- Terms and the label canon are in `glossary/`. Stick to them so nothing diverges.
- The Cyrillic letters are in `font/*.json` (`#` ink, `.` empty).

## Checking your changes

You need Python 3 and a copy of the game. From the repository root:

```sh
./install.sh --dry-run       # Linux/macOS  (install.bat --dry-run on Windows)
```

This extracts the reference strings from the game, checks the translation markup and builds the
bundles, **without touching the game**. If the check found fatal errors (an invented placeholder,
a broken tag, an empty translation) — the build stops and shows where.

A full install — the same script without `--dry-run`.

## Submitting a PR

- One logical change — one PR, where possible.
- In the description, briefly: what and why. A screenshot from the game for text/letter fixes helps a lot.
- CI runs the script compilation and the JSON check. The full markup check needs strings
  from the game and is done locally (see above).

## How it works

The technical underside (how the translation became a native locale, how the banner letters are drawn)
is in the [README](README.md#how-it-works).
