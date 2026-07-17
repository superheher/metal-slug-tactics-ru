#!/usr/bin/env python3
"""Cross-platform installer for the Metal Slug Tactics translator.

Extracts the originals from YOUR copy of the game → checks the markup → builds
the bundles → installs them → enables Russian. The game's assets are not distributed
anywhere: the patch is built in place, from your copy.

  python tools/install.py             install / update the translation
  python tools/install.py --dry-run   build and verify, but do not touch the game
  python tools/install.py --revert    restore the originals from the backup
  python tools/install.py --game DIR  point to the game folder manually

Works on Windows, Linux (Steam/Proton) and macOS (Wine: Whisky, Bottles, CrossOver).
Run again after every Steam update of the game — it restores the native bundles.
"""
import argparse
import json
import os
import platform
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
import extract
import validate
import build as buildmod


def game_running():
    """Best-effort: is the game running (you cannot copy bundles over a live one)."""
    name = "Metal Slug Tactics.exe"
    try:
        if platform.system() == "Windows":
            out = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {name}"],
                                 capture_output=True, text=True).stdout or ""
            return name.lower() in out.lower()
        return subprocess.run(["pgrep", "-f", name],
                              capture_output=True, text=True).returncode == 0
    except Exception:
        return False


def select_russian(options_path):
    """Sets the Russian locale in Save/Options. False if the file does not exist yet."""
    if not options_path or not os.path.isfile(options_path):
        return False
    with open(options_path, encoding="utf-8") as f:
        d = json.load(f)
    entries = d.setdefault("Entries", [])
    value = json.dumps({"useDefault": False, "value": paths.LOCALE_VALUE},
                       separators=(",", ":"))
    for e in entries:
        if e.get("EntryId") == "Locale.option":
            e["Json"] = value
            break
    else:
        entries.append({"EntryId": "Locale.option", "Json": value})
    with open(options_path, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, separators=(",", ":"))
    return True


def disable_bepinex(game_path):
    """BepInEx (the old Google translator) clashes with the native localization — disable it."""
    dll = os.path.join(game_path, "winhttp.dll")
    if os.path.isfile(dll):
        shutil.move(dll, dll + ".disabled")
        return True
    return False


def _build_date():
    try:
        return open(paths.res("build_date.txt"), encoding="utf-8").read().strip()
    except OSError:
        return ""


def _header(title):
    print(f"\n══ {title} ══")


def install(dry_run=False):
    bd = _build_date()
    print("Metal Slug Tactics translator · " + platform.system() + (f" · build {bd}" if bd else ""))
    print(f"game:   {paths.GAME}")
    print(f"work:   {paths.WORK}")

    if not dry_run and game_running():
        sys.exit("\n✗ The game is running — close it and try again.")

    _header("1. game originals and references")
    extract.main()

    _header("2. translation check")
    if validate.main():
        sys.exit("\n✗ Fatal errors in the translation — installation stopped.")

    _header("3. build")
    buildmod.main()

    if dry_run:
        print("\n✓ dry-run: bundles built in build/, the game was left untouched.")
        return 0

    _header("4. install")
    for name in paths.PATCHED:
        shutil.copy2(paths.build(name), os.path.join(paths.AA, name))
        print(f"  ✓ {name}")

    if select_russian(paths.OPTIONS):
        print("  ✓ Russian enabled (to switch back — НАСТРОЙКИ → Язык)")
    else:
        print("  · the settings file does not exist yet — launch the game and choose «Русский»")
        print(f"    in НАСТРОЙКИ → Язык (expected: {paths.OPTIONS})")

    if disable_bepinex(paths.GAME):
        print("  ✓ BepInEx disabled (winhttp.dll → winhttp.dll.disabled)")

    print("\n✓ Done. Launch the game as usual — the language is already Russian.")
    return 0


def revert():
    print(f"Rollback to the originals · game: {paths.GAME}")
    if game_running():
        sys.exit("\n✗ The game is running — close it and try again.")
    restored = 0
    for name in paths.PATCHED:
        b = paths.backup(name)
        if os.path.isfile(b):
            shutil.copy2(b, os.path.join(paths.AA, name))
            print(f"  ✓ restored {name}")
            restored += 1
        else:
            print(f"  · no backup for {name}")
    if not restored:
        sys.exit("\n✗ No backup. Verify the game's file integrity in Steam — "
                 "it will restore the native bundles.")
    print("\n✓ Originals restored. In the game choose English in НАСТРОЙКИ → Язык.")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(add_help=True, description="Metal Slug Tactics translator")
    ap.add_argument("--dry-run", action="store_true",
                    help="build and verify, but do not touch the game")
    ap.add_argument("--revert", action="store_true",
                    help="restore the originals from the backup")
    ap.add_argument("--game", metavar="DIR",
                    help="the MST game folder (if not found automatically)")
    args = ap.parse_args(argv)

    if args.game:
        os.environ["MST_PATH"] = args.game

    try:
        return revert() if args.revert else install(dry_run=args.dry_run)
    except KeyboardInterrupt:
        print("\n aborted.")
        return 130


if __name__ == "__main__":
    frozen = getattr(sys, "frozen", False)
    try:
        code = main()
    except SystemExit as exc:
        code = exc.code
    if frozen:      # double-clicked or launched by the installer: keep the console open
        try:
            input("\nPress Enter to close...")
        except EOFError:
            pass
    sys.exit(code)
