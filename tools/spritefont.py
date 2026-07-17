"""The sprite banner font: taking a letter apart into layers and building a new one in the same style.

The big captions (ХОД ИГРОКА, ПОБЕДА, ПОРАЖЕНИЕ) are drawn NOT as text but as sprites:
the SpriteText component takes a string, splits it into characters and, for each one, pulls
a 25×25 image out of the `SpriteFont` ScriptableObject (a «character code → Sprite» table).

The letter recipe is reverse-engineered from the originals and reproduces H, T, E, F pixel for pixel:
  • fill — 5 gradient bands of 2 rows each;
  • between the bands, DITHERING: 2 rows of a checkerboard, dark colour when (row+column) is even;
  • shadow (120,0,0) — along the TOP and LEFT edge of the fill (not a full ring);
  • white outline (248,248,248) — 1px outward;
  • black border — a ring around the outline PLUS a drop shadow offset down-right.
"""
from PIL import Image, ImageChops
import UnityPy

import paths

FONT_PID = -4169782875964257129          # the SpriteFont ScriptableObject in ui_assets_all
WHITE = (248, 248, 248)
SHADOW = (120, 0, 0)
BLACK = (0, 0, 0)
BANDS = [(248, 208, 48), (248, 144, 24), (248, 104, 0), (240, 48, 0), (176, 0, 0)]


def band_at(r, c):
    """The colour of the letter body. Bands of 2 rows, with a checkerboard between them by parity of (r+c)."""
    if r <= 4:  return BANDS[0]
    if r <= 6:  return BANDS[1] if (r + c) % 2 == 0 else BANDS[0]
    if r <= 8:  return BANDS[1]
    if r <= 10: return BANDS[2] if (r + c) % 2 == 0 else BANDS[1]
    if r <= 12: return BANDS[2]
    if r <= 14: return BANDS[3] if (r + c) % 2 == 0 else BANDS[2]
    if r <= 16: return BANDS[3]
    if r <= 18: return BANDS[4] if (r + c) % 2 == 0 else BANDS[3]
    return BANDS[4]


def _shift(m, dy, dx):
    # np.roll(np.roll(m, dy, rows), dx, cols) with wraparound == ImageChops.offset(m, dx, dy)
    return ImageChops.offset(m, dx, dy)


def _dilate(m):
    """3×3 dilation with wraparound (OR of the shifted neighbourhood)."""
    d = Image.new("L", m.size, 0)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            d = ImageChops.lighter(d, _shift(m, dy, dx))
    return d


def render(fill):
    """A binary 25×25 shape (mode 'L', 0/255) -> a finished RGBA letter in the game's style.

    The masks are 8-bit images holding only 0 or 255; on those, darker=AND, lighter=OR,
    invert=NOT and offset=roll, so this layer algebra matches the boolean-array original
    pixel for pixel.
    """
    AND, OR, NOT = ImageChops.darker, ImageChops.lighter, ImageChops.invert
    shadow = AND(fill, OR(NOT(_shift(fill, 1, 0)), NOT(_shift(fill, 0, 1))))   # top and left edge
    body = AND(fill, NOT(shadow))
    white = AND(_dilate(fill), NOT(fill))
    s1 = OR(fill, white)
    ring = AND(_dilate(s1), NOT(s1))
    s2 = OR(s1, ring)
    drop = AND(_shift(s2, 1, 1), NOT(s2))                                      # the drop shadow
    black = OR(ring, drop)

    out = Image.new("RGBA", (25, 25), (0, 0, 0, 0))
    px = out.load()
    body_p, shadow_p, white_p, black_p = body.load(), shadow.load(), white.load(), black.load()
    for r in range(25):
        for c in range(25):
            if body_p[c, r]:     px[c, r] = (*band_at(r, c), 255)
            elif shadow_p[c, r]: px[c, r] = (*SHADOW, 255)
            elif white_p[c, r]:  px[c, r] = (*WHITE, 255)
            elif black_p[c, r]:  px[c, r] = (*BLACK, 255)
    return out


def open_ui(bundle_path):
    """Opens the ui bundle and pulls out everything needed to work with the sprite font."""
    env = UnityPy.load(bundle_path)
    objs = {o.path_id: o for o in env.objects}

    atlas_obj = next(o for o in env.objects if o.type.name == "SpriteAtlas")
    atlas = atlas_obj.read_typetree()
    key2rect = {str(k): v["textureRect"] for k, v in atlas["m_RenderDataMap"]}

    tex_obj = objs[atlas["m_RenderDataMap"][0][1]["texture"]["m_PathID"]]
    font_obj = objs[FONT_PID]
    font = font_obj.read_typetree()

    # ALL atlas sprites by name — the '?' donor is not wired into the SpriteFont table,
    # but it exists as an object, and it can be referenced.
    by_name = {}
    for o in env.objects:
        if o.type.name != "Sprite":
            continue
        try:
            s = o.read_typetree()
        except Exception:
            continue
        r = key2rect.get(str(s["m_RenderDataKey"]))
        if r:
            by_name[s.get("m_Name", "")] = (
                o.path_id, int(r["x"]), int(r["y"]), int(r["width"]), int(r["height"]))

    # and the ones in the table — by character
    by_char = {}
    for pair in font["_sprites"]["_pairs"]:
        s = objs[pair["_value"]["m_PathID"]].read_typetree()
        r = key2rect[str(s["m_RenderDataKey"])]
        by_char[chr(pair["_key"])] = (
            pair["_value"]["m_PathID"],
            int(r["x"]), int(r["y"]), int(r["width"]), int(r["height"]))

    return env, font_obj, font, tex_obj, by_char, by_name
