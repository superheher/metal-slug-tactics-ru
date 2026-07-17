#!/usr/bin/env python3
"""Builds three bundles from the game's ORIGINALS (backup/) and our sources.

  1. localization-...pt-br...bundle  — Russian text instead of Portuguese
  2. fonts_assets_all.bundle         — Cyrillic in the metal-slug TMP font
  3. ui_assets_all.bundle            — Cyrillic in the sprite banner font

The results go into build/. The game's originals are not modified.
"""
import json
import os
import sys

import numpy as np
from PIL import Image
import UnityPy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
import spritefont


# ─────────────────────────────── 1. text ───────────────────────────────
def build_translation():
    ru = json.load(open(paths.res("translation", "ru.json"), encoding="utf-8"))
    ru[paths.LANG_NAME_ID] = "Русский"      # this is how the language is labelled in the list
    ru[paths.SYSTEM_TPL_ID] = "{Locale}"    # drop the «Системный (...)» wrapper

    tables = json.load(open(paths.build("en_strings.json"), encoding="utf-8"))["tables"]
    want = {name.replace("_en-US", ""): {str(i) for i in rows} for name, rows in tables.items()}

    env = UnityPy.load(paths.backup(paths.PT_BUNDLE))
    replaced = added = 0
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        try:
            t = obj.read_typetree()
        except Exception:
            continue
        if "m_TableData" not in t:
            continue

        base = t.get("m_Name", "").replace("_pt-BR", "")
        have = set()
        for e in t["m_TableData"]:
            i = str(e["m_Id"])
            have.add(i)
            if i in ru:
                e["m_Localized"] = ru[i]
                replaced += 1
        # the Portuguese table is shorter than the English one — append the missing strings
        for i in sorted(want.get(base, set()) - have):
            if i in ru:
                t["m_TableData"].append(
                    {"m_Id": int(i), "m_Localized": ru[i], "m_Metadata": {"m_Items": []}})
                added += 1
        obj.save_typetree(t)

    with open(paths.build(paths.PT_BUNDLE), "wb") as f:
        f.write(env.file.save(packer="original"))
    print(f"  ✓ text: replaced {replaced}, added {added}")


# ──────────────────────────── 2. TMP font ────────────────────────────
def build_tmp_font():
    """Cyrillic in the metal-slug SDF — it renders headings such as «Синхро» in the tables."""
    glyphs = json.load(open(paths.res("font", "tmp_metalslug_7x7.json"), encoding="utf-8"))["letters"]
    SCALE, SIZE = 11, 7

    env = UnityPy.load(paths.backup(paths.FONTS_BUNDLE))
    fobj = tree = None
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        try:
            d = obj.read_typetree()
        except Exception:
            continue
        if d.get("m_Name") == "metal-slug SDF - Regular":
            fobj, tree = obj, d
            break

    pid = tree["m_AtlasTextures"][0]["m_PathID"]
    tobj = next(o for o in env.objects if o.type.name == "Texture2D" and o.path_id == pid)
    tex = tobj.read()
    arr = np.array(tex.image)
    W, H = tree["m_AtlasWidth"], tree["m_AtlasHeight"]
    PAD = tree["m_AtlasPadding"]

    ch = {c["m_Unicode"]: c["m_GlyphIndex"] for c in tree["m_CharacterTable"]}
    gl = {g["m_Index"]: g for g in tree["m_GlyphTable"]}
    tpl = gl[ch[ord("H")]]                      # metrics reference

    occ = np.zeros((H, W), bool)
    for g in tree["m_GlyphTable"]:
        r = g["m_GlyphRect"]
        occ[max(0, r["m_Y"] - PAD):min(H, r["m_Y"] + r["m_Height"] + PAD),
            max(0, r["m_X"] - PAD):min(W, r["m_X"] + r["m_Width"] + PAD)] = True
    cell = SIZE * SCALE + 2 * PAD
    free = []
    for y in range(0, H - cell, 8):
        for x in range(0, W - cell, 8):
            if not occ[y:y + cell, x:x + cell].any():
                free.append((x + PAD, y + PAD))
                occ[y:y + cell, x:x + cell] = True

    idx = max(g["m_Index"] for g in tree["m_GlyphTable"]) + 1
    reused = drawn = 0

    for cyr, lat in paths.SAME_AS_LATIN.items():      # 11 letters — without a single pixel
        gi = ch[ord(lat)]
        for u in (ord(cyr), ord(cyr.lower())):
            if u not in ch:
                tree["m_CharacterTable"].append(
                    {"m_ElementType": 1, "m_Unicode": u, "m_GlyphIndex": gi, "m_Scale": 1.0})
        reused += 1

    for letter, rows in glyphs.items():
        if letter in paths.SAME_AS_LATIN:
            continue
        if not free:
            sys.exit("✗ the font atlas ran out of space")
        gx, gy = free.pop(0)
        bmp = np.zeros((SIZE, SIZE), np.uint8)
        for r, line in enumerate(rows):
            for c, v in enumerate(line[:SIZE]):
                if v == "#":
                    bmp[r, c] = 255
        big = np.kron(bmp, np.ones((SCALE, SCALE), np.uint8))
        gh, gw = big.shape
        arr[H - gy - gh:H - gy, gx:gx + gw, 3] = big          # data in alpha, atlas bottom-up

        g = json.loads(json.dumps(tpl))
        g["m_Index"] = idx
        g["m_GlyphRect"] = {"m_X": gx, "m_Y": gy, "m_Width": gw, "m_Height": gh}
        tree["m_GlyphTable"].append(g)
        for u in (ord(letter), ord(letter.lower())):
            if u not in ch:
                tree["m_CharacterTable"].append(
                    {"m_ElementType": 1, "m_Unicode": u, "m_GlyphIndex": idx, "m_Scale": 1.0})
        idx += 1
        drawn += 1

    tree["m_CharacterTable"].sort(key=lambda c: c["m_Unicode"])
    fobj.save_typetree(tree)
    tex.image = Image.fromarray(arr, "RGBA")
    tex.save()
    with open(paths.build(paths.FONTS_BUNDLE), "wb") as f:
        f.write(env.file.save(packer="original"))
    print(f"  ✓ TMP font: reused {reused}, drawn {drawn}")


# ──────────────────────── 3. sprite font ────────────────────────
def build_sprite_font():
    """Cyrillic in the banner font: ХОД ИГРОКА, ПОБЕДА, ПОРАЖЕНИЕ, ВНИМАНИЕ!, etc.

    There are not enough donor letters in the font (see the bans in paths.py), so three letters
    take over UNUSED sprites (selector1..3): each is given a copy of a letter's geometry,
    and its rectangle is relocated to free space in the atlas.
    """
    cyr = json.load(open(paths.res("font", "sprite_banner_25x25.json"), encoding="utf-8"))["letters"]

    env, fobj, font, tobj, by_char, by_name = spritefont.open_ui(paths.backup(paths.UI_BUNDLE))
    objs = {o.path_id: o for o in env.objects}
    sa_obj = next(o for o in env.objects if o.type.name == "SpriteAtlas")
    sa = sa_obj.read_typetree()
    tex = tobj.read()
    atlas = np.array(tex.image)
    H, W = atlas.shape[:2]

    # the reference geometry of a letter
    src_pid = by_name[paths.GEOM_SOURCE][0]
    geom = objs[src_pid].read_typetree()

    # key -> atlas entry map, and the reference entry
    rdm = {str(k): (k, v) for k, v in sa["m_RenderDataMap"]}
    src_key = str(objs[src_pid].read_typetree()["m_RenderDataKey"])
    src_entry = rdm[src_key][1]

    # free cells in the atlas texture
    occ = np.zeros((H, W), bool)
    for _, v in sa["m_RenderDataMap"]:
        r = v["textureRect"]
        x, y, w, h = int(r["x"]), int(r["y"]), int(r["width"]), int(r["height"])
        occ[max(0, H - y - h - 2):H - y + 2, max(0, x - 2):x + w + 2] = True
    free = []
    for y in range(0, H - 29, 4):
        for x in range(0, W - 29, 4):
            if not occ[y:y + 29, x:x + 29].any():
                free.append((x + 2, H - y - 27))          # Unity coordinates: bottom-up
                occ[y:y + 29, x:x + 29] = True

    regeom = 0
    for letter, donor in paths.SPRITE_DONORS.items():
        rows = cyr.get(letter)
        if not rows:
            sys.exit(f"✗ no shape for the letter {letter}")
        if donor not in by_name:
            sys.exit(f"✗ no donor sprite {donor}")
        fill = np.array([[c == "#" for c in r.ljust(25, ".")[:25]] for r in rows[:25]], bool)
        img = spritefont.render(fill)
        pid, x, y, w, h = by_name[donor]

        if donor in paths.REGEOM:
            # a sprite not from the font: copy the letter's geometry, keeping its own name and key
            if not free:
                sys.exit("✗ the atlas ran out of free space")
            nx, ny = free.pop(0)
            d = objs[pid].read_typetree()
            key, name = d["m_RenderDataKey"], d["m_Name"]
            new = json.loads(json.dumps(geom, default=lambda o: o.hex()))
            d2 = objs[src_pid].read_typetree()          # a fresh copy with the bytes
            d2["m_Name"] = name
            d2["m_RenderDataKey"] = key
            objs[pid].save_typetree(d2)
            # the rectangle in the atlas -> the new place
            e = json.loads(json.dumps(src_entry, default=str))
            entry = rdm[str(key)][1]
            entry["textureRect"] = {"x": float(nx), "y": float(ny), "width": 25.0, "height": 25.0}
            entry["textureRectOffset"] = dict(src_entry["textureRectOffset"])
            entry["uvTransform"] = dict(src_entry["uvTransform"])
            entry["settingsRaw"] = src_entry["settingsRaw"]
            entry["downscaleMultiplier"] = src_entry["downscaleMultiplier"]
            x, y, w, h = nx, ny, 25, 25
            regeom += 1

        atlas[H - y - h:H - y, x:x + w] = img

    sa_obj.save_typetree(sa)

    pairs = font["_sprites"]["_pairs"]
    have = {p["_key"] for p in pairs}
    mapping = {c: by_char[l][0] for c, l in paths.SAME_AS_LATIN_SPRITE.items()}
    mapping.update({c: by_name[d][0] for c, d in paths.SPRITE_DONORS.items()})
    for cyr_c, pid in mapping.items():
        for u in (ord(cyr_c), ord(cyr_c.lower())):
            if u not in have:
                pairs.append({"_key": u, "_value": {"m_FileID": 0, "m_PathID": pid}})
                have.add(u)
    pairs.sort(key=lambda p: p["_key"])

    fobj.save_typetree(font)
    tex.image = Image.fromarray(atlas, "RGBA")
    tex.save()
    with open(paths.build(paths.UI_BUNDLE), "wb") as f:
        f.write(env.file.save(packer="original"))
    print(f"  ✓ sprite font: reused {len(paths.SAME_AS_LATIN_SPRITE)}, "
          f"drawn {len(paths.SPRITE_DONORS)} (of which {regeom} on unused sprites)")


def main():
    os.makedirs(paths.BUILD, exist_ok=True)
    for name in paths.PATCHED:
        if not os.path.exists(paths.backup(name)):
            sys.exit(f"✗ No original {name} — run tools/extract.py first")
    print("build:")
    build_translation()
    build_tmp_font()
    build_sprite_font()
    print(f"\n  done -> {paths.BUILD}")


if __name__ == "__main__":
    main()
