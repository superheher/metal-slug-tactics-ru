"""Paths and shared constants: where the game is, where the repo is, what gets built into what."""
import glob
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
BACKUP = os.path.join(ROOT, "backup")

# the bundles we touch
PT_BUNDLE = "localization-string-tables-portuguese(brazil)(pt-br)_assets_all.bundle"
EN_BUNDLE = "localization-string-tables-english(unitedstates)(en-us)_assets_all.bundle"
FONTS_BUNDLE = "fonts_assets_all.bundle"
UI_BUNDLE = "ui_assets_all.bundle"
PATCHED = [PT_BUNDLE, FONTS_BUNDLE, UI_BUNDLE]

# Cyrillic letters whose shape matches a Latin one — these need not a single pixel,
# they simply reference the ready-made glyphs.
SAME_AS_LATIN = {"А": "A", "В": "B", "Е": "E", "К": "K", "М": "M", "Н": "H",
                 "О": "O", "Р": "P", "С": "C", "Т": "T", "Х": "X"}
# The sprite font adds З as well — in this typeface it is indistinguishable from the digit 3.
SAME_AS_LATIN_SPRITE = {**SAME_AS_LATIN, "З": "3"}
# Letters we had to draw, and the donor sprites used for them.
# The donors are chosen so they appear in NONE of the five sprite captions
# in any of the game's languages — so English does not suffer from the swap.
SPRITE_DONORS = {"Б": "G", "Г": "J", "Д": "Q", "Ж": "W", "И": "Z", "Й": "!", "П": "0", "Ц": "1"}

# Two service localization strings
LANG_NAME_ID = "240000458967474176"      # the language name in the list ("English" -> "Русский")
SYSTEM_TPL_ID = "167188675005767680"     # the "System ({Locale})" template -> just "{Locale}"

LOCALE_VALUE = "Portuguese (Brazil) (pt-BR)"   # the game stores the locale's ASSET NAME, not a code


def find_game():
    """Finds the MST folder. The path can be set explicitly: MST_PATH=/path/to/MST"""
    if os.environ.get("MST_PATH"):
        p = os.environ["MST_PATH"]
        if os.path.isdir(p):
            return p
        sys.exit(f"✗ MST_PATH points nowhere: {p}")

    for pat in (
        "~/Games/steam/Bottles/*/drive_c/Program Files (x86)/Steam/steamapps/common/MST",
        "~/Library/Containers/*/Bottles/*/drive_c/Program Files (x86)/Steam/steamapps/common/MST",
        "~/Library/Application Support/*/Bottles/*/drive_c/Program Files (x86)/Steam/steamapps/common/MST",
    ):
        hits = glob.glob(os.path.expanduser(pat))
        if hits:
            return hits[0]
    sys.exit("✗ Game not found. Set the path: MST_PATH=/path/to/MST")


GAME = find_game()
AA = os.path.join(GAME, "Metal Slug Tactics_Data", "StreamingAssets", "aa", "StandaloneWindows64")

_prefix = GAME.split("/drive_c/")[0] if "/drive_c/" in GAME else None
OPTIONS = os.path.join(
    _prefix, "drive_c", "users", os.environ.get("USER", ""),
    "AppData", "LocalLow", "Leikir Studio", "Metal Slug Tactics", "Save", "Options",
) if _prefix else None


def game(name):
    return os.path.join(AA, name)


def backup(name):
    return os.path.join(BACKUP, name)


def build(name):
    return os.path.join(BUILD, name)
