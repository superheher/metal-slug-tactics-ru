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
import numpy as np
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
    return np.roll(np.roll(m, dy, 0), dx, 1)


def _dilate(m):
    d = np.zeros_like(m)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            d |= _shift(m, dy, dx)
    return d


def layers(sprite):
    """RGBA 25×25 -> (fill, white outline, black border). Fill = body + shadow."""
    rgb = sprite[..., :3].astype(int)
    opaque = sprite[..., 3] > 128
    black = opaque & (rgb.max(2) < 50)
    white = opaque & (rgb.min(2) > 200)
    return opaque & ~black & ~white, white, black


def render(fill):
    """A binary 25×25 shape -> a finished RGBA letter in the game's style."""
    shadow = fill & (~_shift(fill, 1, 0) | ~_shift(fill, 0, 1))   # top and left edge
    body = fill & ~shadow
    white = _dilate(fill) & ~fill
    s1 = fill | white
    ring = _dilate(s1) & ~s1
    s2 = s1 | ring
    drop = _shift(s2, 1, 1) & ~s2                                  # the drop shadow
    black = ring | drop

    out = np.zeros((25, 25, 4), np.uint8)
    for r in range(25):
        for c in range(25):
            if body[r, c]:     out[r, c] = (*band_at(r, c), 255)
            elif shadow[r, c]: out[r, c] = (*SHADOW, 255)
            elif white[r, c]:  out[r, c] = (*WHITE, 255)
            elif black[r, c]:  out[r, c] = (*BLACK, 255)
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

    rects = {}
    for pair in font["_sprites"]["_pairs"]:
        s = objs[pair["_value"]["m_PathID"]].read_typetree()
        r = key2rect[str(s["m_RenderDataKey"])]
        rects[chr(pair["_key"])] = (
            pair["_value"]["m_PathID"],
            int(r["x"]), int(r["y"]), int(r["width"]), int(r["height"]),
        )
    return env, font_obj, font, tex_obj, rects


def grab(atlas_arr, rect, height):
    """Cuts a sprite out of the atlas texture (Unity's origin is at the bottom)."""
    _, x, y, w, h = rect
    return atlas_arr[height - y - h:height - y, x:x + w].copy()
