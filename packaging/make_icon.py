#!/usr/bin/env python3
"""Generate the exe / window icon (mst-ru.ico) from the poster art.

Input:  packaging/art/poster.png
Output: packaging/art/mst-ru.ico          (Marco, all sizes; small ones sharpened)
        packaging/art/preview-icon.png     (review only, git-ignored)

Run:  python packaging/make_icon.py
"""
import os
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, "art")
SIZES = [256, 128, 64, 48, 32, 24, 16]


def square_frac(im, cx, cy, half):
    """Square crop centred at (cx, cy) with side 2*half, all as fractions of height."""
    w, h = im.size
    s = round(half * h)
    x, y = round(cx * w), round(cy * h)
    return im.crop((x - s, y - s, x + s, y + s))


def main():
    poster = Image.open(os.path.join(ART, "poster.png")).convert("RGBA")
    # tighter crop on Marco's face so it still reads at 16-32 px
    base = square_frac(poster, cx=0.47, cy=0.66, half=0.13).resize((256, 256), Image.LANCZOS)

    imgs = []
    for s in SIZES:
        im = base.resize((s, s), Image.LANCZOS)
        if s <= 48:                       # sharpen the small sizes so the taskbar icon isn't mushy
            im = im.filter(ImageFilter.UnsharpMask(radius=1.0, percent=140, threshold=1))
        imgs.append(im)
    imgs[0].save(os.path.join(ART, "mst-ru.ico"), format="ICO",
                 sizes=[(s, s) for s in SIZES], append_images=imgs[1:])

    # preview strip
    pad, gap = 20, 20
    c = Image.new("RGB", (pad * 2 + sum(SIZES) + gap * (len(SIZES) - 1), 256 + pad * 2), (230, 230, 230))
    x = pad
    for im in imgs:
        s = im.size[0]
        c.paste(im.convert("RGB"), (x, pad + 256 - s))
        x += s + gap
    c.save(os.path.join(ART, "preview-icon.png"))
    print("wrote mst-ru.ico (sizes", ",".join(map(str, SIZES)) + ") + preview-icon.png")


if __name__ == "__main__":
    main()
