#!/usr/bin/env python3
"""Generate the exe icon (mst-ru.ico) from the poster art.

Input:  packaging/art/poster.png
Output: packaging/art/mst-ru.ico   (Marco, multi-size)
        packaging/art/preview-icon.png   (review only, git-ignored)

Run:  python packaging/make_icon.py
"""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, "art")


def square_frac(im, cx, cy, half):
    """Square crop centred at (cx, cy) with side 2*half, all as fractions of height."""
    w, h = im.size
    s = round(half * h)
    x, y = round(cx * w), round(cy * h)
    return im.crop((x - s, y - s, x + s, y + s))


def main():
    poster = Image.open(os.path.join(ART, "poster.png")).convert("RGB")
    marco = square_frac(poster, cx=0.47, cy=0.68, half=0.17).resize((256, 256), Image.LANCZOS)
    marco.save(os.path.join(ART, "mst-ru.ico"),
               sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])

    sizes = [16, 24, 32, 48, 64, 128, 256]
    pad, gap = 20, 20
    c = Image.new("RGB", (pad * 2 + sum(sizes) + gap * (len(sizes) - 1), 256 + pad * 2), (230, 230, 230))
    x = pad
    for s in sizes:
        c.paste(marco.resize((s, s), Image.LANCZOS), (x, pad + 256 - s))
        x += s + gap
    c.save(os.path.join(ART, "preview-icon.png"))
    print("wrote mst-ru.ico + preview-icon.png")


if __name__ == "__main__":
    main()
