"""Paths and shared constants: where the game is, where the saves are, what gets built into what.

Cross-platform: native Windows, Linux (native Steam / Proton),
macOS + Wine (Whisky, Bottles, CrossOver). Works both as an ordinary module
and inside a PyInstaller-built installer (see RES/WORK below).
"""
import glob
import os
import platform
import re
import sys

# ─────────────────────────── resources and work folder ───────────────────────────
# RES  — where the translation sources are READ from (translation/, font/). In a normal
#        run this is the repository root; in a built exe — the unpacked _MEIPASS.
# WORK — where backup/ and build/ are WRITTEN. In the repository this is its own root (the
#        files are git-ignored); in a built exe — the user's data folder, so as not to
#        write inside the executable and so the backup survives a restart.
_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(_HERE)
FROZEN = getattr(sys, "frozen", False)


def _user_data_dir():
    home = os.path.expanduser("~")
    sysname = platform.system()
    if sysname == "Windows":
        base = os.environ.get("LOCALAPPDATA") or os.path.join(home, "AppData", "Local")
    elif sysname == "Darwin":
        base = os.path.join(home, "Library", "Application Support")
    else:
        base = os.environ.get("XDG_DATA_HOME") or os.path.join(home, ".local", "share")
    return os.path.join(base, "mst-ru")


if FROZEN:
    RES = getattr(sys, "_MEIPASS", ROOT)
    WORK = _user_data_dir()
else:
    RES = ROOT
    WORK = ROOT

BUILD = os.path.join(WORK, "build")
BACKUP = os.path.join(WORK, "backup")


def res(*parts):
    """Path to a translation/font source (read-only)."""
    return os.path.join(RES, *parts)


# ─────────────────────────────── bundles ───────────────────────────────
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
# Letters we had to draw, and the donor sprites used for them — BY sprite NAME.
#
# ⚠️ WHAT MUST NOT BE TAKEN (verified by a full sweep of all 235 bundles):
#
#   DIGITS 0-9 — they draw the numbers on the tactical map:
#       ExitZoneView (timer), LimitedDurationRoomsView (turns remaining),
#       DelayedVehicleInvocation (turns until the vehicle arrives).
#
#   THE ! SIGN — is in the «WARNING!» / «ВНИМАНИЕ!» caption. It is drawn with sprites through
#       a different binding: LocalizeStringTarget + StringTargetSpriteText (not LocalizeSpriteText).
#
#   THE LETTERS A C D E F G I L M N O P R S T U V W Y — are needed by the English captions:
#       PLACE UNITS · PLAYER TURN · ENEMY TURN · VICTORY · DEFEAT · WARNING!
#       (W and G — precisely from WARNING; they are easy to step on.)
#
#   THE LETTERS B H K X and the digit 3 — are referenced by Cyrillic (В Н К Х З).
#
# FREE: J Q Z (do not appear in the sprite captions in any language),
#   ui_fontBigInterrogation (the «?» sign — not wired to the SpriteFont at all, 0 references),
#   selector1..3 (31×31, 0 references in the whole game — each is given a copy of a letter's
#   geometry, and its rectangle is relocated to free space in the atlas).
SPRITE_DONORS = {
    "Б": "ui_fontBigJ",
    "Г": "ui_fontBigQ",
    "Д": "ui_fontBigZ",
    "Ж": "ui_fontBigInterrogation",
    "И": "selector1",
    "Л": "selector2",
    "П": "selector3",
}
# Donors whose geometry must be REMADE to fit a 25×25 letter (they are not from the font).
REGEOM = {"selector1", "selector2", "selector3"}
GEOM_SOURCE = "ui_fontBigA"      # the reference geometry of a letter

# Ц and Й are drawn (see font/sprite_banner_25x25.json), but are not used in the captions.

# Two service localization strings
LANG_NAME_ID = "240000458967474176"      # the language name in the list ("English" -> "Русский")
SYSTEM_TPL_ID = "167188675005767680"     # the "System ({Locale})" template -> just "{Locale}"

LOCALE_VALUE = "Portuguese (Brazil) (pt-BR)"   # the game stores the locale's ASSET NAME, not a code

# ─────────────────────────────── game discovery ───────────────────────────────
APPID = "1590760"        # Metal Slug Tactics on Steam
INSTALLDIR = "MST"       # the install folder name in steamapps/common (the same on every OS)
_DATA = "Metal Slug Tactics_Data"
_AA_TAIL = os.path.join(_DATA, "StreamingAssets", "aa", "StandaloneWindows64")


def _looks_like_game(path):
    """Does the folder actually contain the game with its Addressables bundles?"""
    return bool(path) and os.path.isdir(os.path.join(path, _AA_TAIL))


def _steam_roots():
    """Possible Steam install roots for the current OS."""
    home = os.path.expanduser("~")
    sysname = platform.system()
    roots = []
    if sysname == "Windows":
        for base in (os.environ.get("ProgramFiles(x86)"), os.environ.get("ProgramFiles"),
                     r"C:\Program Files (x86)", r"C:\Program Files"):
            if base:
                roots.append(os.path.join(base, "Steam"))
        for drive in "CDEFGH":
            roots.append(rf"{drive}:\SteamLibrary")
            roots.append(rf"{drive}:\Steam")
    elif sysname == "Darwin":
        roots.append(os.path.join(home, "Library", "Application Support", "Steam"))
    else:  # Linux
        roots += [os.path.join(home, ".steam", "steam"),
                  os.path.join(home, ".steam", "root"),
                  os.path.join(home, ".local", "share", "Steam"),
                  os.path.join(home, ".var", "app", "com.valvesoftware.Steam", "data", "Steam")]
    seen, out = set(), []
    for r in roots:
        if r and r not in seen:
            seen.add(r)
            out.append(r)
    return out


def _steam_libraries(steam_root):
    """All Steam libraries from libraryfolders.vdf (plus the root itself)."""
    libs = [steam_root]
    for vdf in (os.path.join(steam_root, "steamapps", "libraryfolders.vdf"),
                os.path.join(steam_root, "config", "libraryfolders.vdf")):
        try:
            txt = open(vdf, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        libs += re.findall(r'"path"\s*"([^"]+)"', txt.replace("\\\\", "\\"))
    seen, out = set(), []
    for l in libs:
        if l and l not in seen:
            seen.add(l)
            out.append(l)
    return out


def _wine_candidates():
    """Paths to the game inside Wine prefixes (macOS/Linux): Whisky, Bottles, CrossOver."""
    tail = os.path.join("drive_c", "Program Files (x86)", "Steam",
                        "steamapps", "common", INSTALLDIR)
    pats = [
        "~/Games/steam/Bottles/*/" + tail,
        "~/Library/Application Support/com.isaacmarovitz.Whisky/Bottles/*/" + tail,
        "~/Library/Application Support/CrossOver/Bottles/*/" + tail,
        "~/Library/Containers/*/Bottles/*/" + tail,
        "~/Library/Application Support/*/Bottles/*/" + tail,
        "~/.var/app/com.usebottles.bottles/data/bottles/bottles/*/" + tail,
        "~/.local/share/bottles/bottles/*/" + tail,
    ]
    hits = []
    for p in pats:
        hits += glob.glob(os.path.expanduser(p))
    return hits


def find_game():
    """Finds the MST folder. The path can be set explicitly: MST_PATH=/path/to/MST"""
    override = os.environ.get("MST_PATH")
    if override:
        if _looks_like_game(override):
            return override
        sys.exit(f"✗ MST_PATH does not look like the game folder: {override}\n"
                 f"  A MST folder with a «{_DATA}» subfolder is needed.")

    candidates = []
    for root in _steam_roots():
        for lib in _steam_libraries(root):
            candidates.append(os.path.join(lib, "steamapps", "common", INSTALLDIR))
    candidates += _wine_candidates()

    seen = set()
    for c in candidates:
        if c in seen:
            continue
        seen.add(c)
        if _looks_like_game(c):
            return c

    sysname = platform.system()
    hint = ("MST_PATH=C:\\path\\to\\steamapps\\common\\MST" if sysname == "Windows"
            else "MST_PATH=/path/to/steamapps/common/MST")
    sys.exit("✗ Metal Slug Tactics not found.\n"
             f"  Set the path explicitly:  {hint}")


def find_options(game_path):
    """The game's settings file Save/Options (it stores the chosen locale).

    It may not exist yet if the game has never been launched — then the
    expected path is returned, and the decision (create/skip) is up to the caller.
    """
    leikir = os.path.join("AppData", "LocalLow", "Leikir Studio",
                          "Metal Slug Tactics", "Save", "Options")

    if platform.system() == "Windows":
        profile = os.environ.get("USERPROFILE") or os.path.expanduser("~")
        return os.path.join(profile, leikir)

    # Wine/CrossOver: the game lives inside the prefix (…/drive_c/…)
    marker = os.sep + "drive_c" + os.sep
    if marker in game_path + os.sep:
        prefix = game_path.split(marker)[0]
        got = _options_in_prefix(prefix, leikir)
        if got:
            return got

    # Linux + Proton: the game is in the library, the prefix is in compatdata/<appid>/pfx
    parts = game_path.split(os.sep + "steamapps" + os.sep)
    if len(parts) >= 2:
        pfx = os.path.join(parts[0], "steamapps", "compatdata", APPID, "pfx")
        got = _options_in_prefix(pfx, leikir)
        if got:
            return got

    # A native Linux Unity build (unlikely for MST)
    xdg = os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.path.expanduser("~"), ".config")
    return os.path.join(xdg, "unity3d", "Leikir Studio", "Metal Slug Tactics", "Save", "Options")


def _options_in_prefix(prefix, leikir_tail):
    """Looks for Save/Options among the Wine prefix's users; otherwise builds the expected path."""
    hits = glob.glob(os.path.join(prefix, "drive_c", "users", "*", leikir_tail))
    if hits:
        return hits[0]
    users = [u for u in glob.glob(os.path.join(prefix, "drive_c", "users", "*"))
             if os.path.basename(u) != "Public"]
    if not users:
        return None
    prefer = [os.environ.get("USER") or "", "steamuser", "crossover"]
    users.sort(key=lambda u: prefer.index(os.path.basename(u))
               if os.path.basename(u) in prefer else len(prefer))
    return os.path.join(users[0], leikir_tail)


# ─────────────────── computed paths (lazy initialization) ───────────────────
# GAME / AA / OPTIONS are computed on first access, not on import: this way the module
# can be imported even when the game has not been found yet (the installer needs this
# for graceful error handling).
_GAME = None


def _init():
    global _GAME, GAME, AA, OPTIONS
    if _GAME is None:
        _GAME = find_game()
        GAME = _GAME
        AA = os.path.join(GAME, _AA_TAIL)
        OPTIONS = find_options(GAME)
    return _GAME


def __getattr__(name):      # PEP 562: lazy module attributes
    if name in ("GAME", "AA", "OPTIONS"):
        _init()
        return globals()[name]
    raise AttributeError(f"module 'paths' has no attribute {name!r}")


def game(name):
    _init()
    return os.path.join(AA, name)


def backup(name):
    return os.path.join(BACKUP, name)


def build(name):
    return os.path.join(BUILD, name)
