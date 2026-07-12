#!/bin/bash
# Metal Slug Tactics translator: extract originals -> verify -> build -> install.
# Run after every Steam update of the game — it restores the native bundles.
set -e
cd "$(dirname "$0")"

VENV=".venv"
PY="$VENV/bin/python"

if [ ! -x "$PY" ]; then
    echo "→ creating the environment and installing dependencies"
    python3 -m venv "$VENV"
    "$VENV/bin/pip" install -q --disable-pip-version-check UnityPy numpy Pillow
fi

# We look specifically for the game's process under Wine: its command line starts with 'C:\'.
# Plain 'Metal Slug Tactics' will not do — pgrep would also match the shell that contains the words.
if pgrep -f '^C:.*Metal Slug Tactics\.exe' >/dev/null; then
    echo "✗ The game is running — close it first"
    exit 1
fi

echo
echo "══ 1. game originals and references ══"
"$PY" tools/extract.py

echo
echo "══ 2. translation check ══"
"$PY" tools/validate.py

echo
echo "══ 3. build ══"
"$PY" tools/build.py

echo
echo "══ 4. install ══"
AA=$("$PY" -c "import sys; sys.path.insert(0,'tools'); import paths; print(paths.AA)")
OPT=$("$PY" -c "import sys; sys.path.insert(0,'tools'); import paths; print(paths.OPTIONS or '')")
MST=$("$PY" -c "import sys; sys.path.insert(0,'tools'); import paths; print(paths.GAME)")

for f in build/*.bundle; do
    cp "$f" "$AA/$(basename "$f")"
    echo "  ✓ $(basename "$f")"
done

# Enable Russian right away. The game stores the locale's ASSET NAME, not a code — it ignores «pt-BR».
if [ -n "$OPT" ] && [ -f "$OPT" ]; then
"$PY" - "$OPT" <<'PY'
import sys, json
p = sys.argv[1]
d = json.load(open(p, encoding='utf-8'))
for e in d["Entries"]:
    if e["EntryId"] == "Locale.option":
        e["Json"] = json.dumps({"useDefault": False, "value": "Portuguese (Brazil) (pt-BR)"},
                               separators=(',', ':'))
json.dump(d, open(p, "w", encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
PY
    echo "  ✓ Russian enabled (you can switch back in SETTINGS)"
fi

# BepInEx with the old Google translator is unnecessary and clashes with the native localization.
if [ -f "$MST/winhttp.dll" ]; then
    mv "$MST/winhttp.dll" "$MST/winhttp.dll.disabled"
    echo "  ✓ BepInEx disabled"
fi

echo
echo "Done. Launching the game (Steam must be up):"
echo '  WhiskyCmd run steam "C:\Program Files (x86)\Steam\steamapps\common\MST\Metal Slug Tactics.exe" \'
echo '    -- -screen-fullscreen 0 -screen-width 1280 -screen-height 720'
