#!/usr/bin/env python3
"""Prepares everything needed for the build from YOUR copy of the game.

  1. Saves the originals of the three bundles into backup/ — but only if the game
     currently holds the originals, not our patch. This is how a Steam update is
     absorbed: it restores the game's native bundles, and the backup refreshes itself.
  2. Extracts the reference data into build/:
       en_strings.json  — the English strings (reference for checking markup)
       latin_ref.json   — the Latin 7×7 glyphs from the metal-slug font

The game's assets stay on your machine: none of them ever end up in the repository.
"""
import json
import os
import shutil
import sys

import numpy as np
import UnityPy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths


def is_patched(bundle_path):
    """Our bundle or the native one? Look for Cyrillic in the string tables / font."""
    env = UnityPy.load(bundle_path)
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        try:
            d = obj.read_typetree()
        except Exception:
            continue
        for e in d.get("m_TableData", []):
            s = e.get("m_Localized") or ""
            if any("А" <= ch <= "я" for ch in s):
                return True
        for c in d.get("m_CharacterTable", []):
            if 0x0410 <= c["m_Unicode"] <= 0x044F:
                return True
        if "_sprites" in d:
            for p in d["_sprites"].get("_pairs", []):
                if 0x0410 <= p["_key"] <= 0x044F:
                    return True
    return False


def backup_originals():
    os.makedirs(paths.BACKUP, exist_ok=True)
    for name in paths.PATCHED:
        src, dst = paths.game(name), paths.backup(name)
        if not os.path.exists(src):
            sys.exit(f"✗ No bundle in the game: {src}")
        if is_patched(src):
            if not os.path.exists(dst):
                sys.exit(f"✗ The game already has our patch, and there is no backup: {name}\n"
                         f"  Verify the game's file integrity in Steam and try again.")
            print(f"  = {name}: the game has our patch, backup is in place")
        else:
            shutil.copy2(src, dst)
            print(f"  ✓ {name}: saved the original ({os.path.getsize(dst):,} B)")


def extract_strings():
    """The English string tables -> build/en_strings.json"""
    env = UnityPy.load(paths.game(paths.EN_BUNDLE))
    tables = {}
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        try:
            d = obj.read_typetree()
        except Exception:
            continue
        if "m_TableData" not in d:
            continue
        rows = {e["m_Id"]: e["m_Localized"] for e in d["m_TableData"] if e.get("m_Localized")}
        if rows:
            tables[d.get("m_Name", "")] = rows
    total = sum(len(v) for v in tables.values())
    with open(paths.build("en_strings.json"), "w") as f:
        json.dump({"tables": tables}, f, ensure_ascii=False)
    print(f"  ✓ en_strings.json: {len(tables)} tables, {total} strings")


def extract_latin_font():
    """The Latin 7×7 glyphs from the metal-slug TMP font -> build/latin_ref.json"""
    env = UnityPy.load(paths.backup(paths.FONTS_BUNDLE))
    font = tex = None
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        try:
            d = obj.read_typetree()
        except Exception:
            continue
        if d.get("m_Name") == "metal-slug SDF - Regular":
            font = d
            break
    pid = font["m_AtlasTextures"][0]["m_PathID"]
    tex = next(o for o in env.objects if o.type.name == "Texture2D" and o.path_id == pid).read()

    a = np.array(tex.image)[..., 3]
    H = a.shape[0]
    ch = {c["m_Unicode"]: c["m_GlyphIndex"] for c in font["m_CharacterTable"]}
    gl = {g["m_Index"]: g for g in font["m_GlyphTable"]}

    ref = {}
    for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789":
        if ord(c) not in ch:
            continue
        r = gl[ch[ord(c)]]["m_GlyphRect"]
        x, y, w, h = r["m_X"], r["m_Y"], r["m_Width"], r["m_Height"]
        b = (a[H - y - h:H - y, x:x + w] >= 128)[::11, ::11]     # the source grid: pixel = 11×11
        ref[c] = ["".join("#" if v else "." for v in row) for row in b]
    with open(paths.build("latin_ref.json"), "w") as f:
        json.dump({"scale": 11, "size": 7, "glyphs": ref}, f, ensure_ascii=False, indent=1)
    print(f"  ✓ latin_ref.json: {len(ref)} Latin 7×7 glyphs")


def main():
    os.makedirs(paths.BUILD, exist_ok=True)
    print(f"game: {paths.GAME}\n")
    print("originals:")
    backup_originals()
    print("\nreferences:")
    extract_strings()
    extract_latin_font()


if __name__ == "__main__":
    main()
