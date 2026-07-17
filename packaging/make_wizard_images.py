#!/usr/bin/env python3
"""Generate the Inno Setup wizard images and the app icon from the source art.

Inputs  (packaging/art/):
  poster.png   1024x1536  vertical poster (logo + «РУСИФИКАТОР» + heroes)
  banner.png   2048x768   wide banner (logo left, heroes right)

Outputs (packaging/art/):
  wizard-image.bmp   328x628   -> Inno WizardImageFile   (Welcome / Finished hero, ratio 164:314)
  banner-wide.bmp    994x373   -> optional full-width header (Welcome page)
  mst-ru.ico         multi     -> setup + patcher icon (Marco)
  preview-*.png                -> mock previews for review (not shipped)

Run:  python packaging/make_wizard_images.py
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, "art")


def _font(bold=False, size=13):
    for p in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold
              else "/System/Library/Fonts/Supplemental/Arial.ttf",
              "/Library/Fonts/Arial.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
              else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def cover_crop(im, ratio, ax=0.5, ay=0.5):
    """Crop im to the given w/h ratio (fills, no distortion). ax/ay = 0..1 anchor
    for the trimmed axis (0.5 = centred)."""
    w, h = im.size
    if w / h > ratio:                 # too wide -> trim sides
        nw = round(h * ratio)
        x = round((w - nw) * ax)
        return im.crop((x, 0, x + nw, h))
    nh = round(w / ratio)             # too tall -> trim top/bottom
    y = round((h - nh) * ay)
    return im.crop((0, y, w, y + nh))


def square_frac(im, cx, cy, half):
    """Square crop centred at (cx, cy) with side 2*half, all as fractions of height."""
    w, h = im.size
    s = round(half * h)
    x, y = round(cx * w), round(cy * h)
    return im.crop((x - s, y - s, x + s, y + s))


def fit_blur(im, w, h):
    """Fit the WHOLE image into w x h (nothing cropped), filling the letterbox with a
    blurred, darkened cover of the same image — so there are no hard bars."""
    bg = cover_crop(im, w / h).resize((w, h), Image.LANCZOS).filter(ImageFilter.GaussianBlur(22))
    bg = ImageEnhance.Brightness(bg).enhance(0.55)
    fg = im.copy()
    fg.thumbnail((w, h), Image.LANCZOS)
    bg.paste(fg, ((w - fg.width) // 2, (h - fg.height) // 2))
    return bg


def main():
    poster = Image.open(os.path.join(ART, "poster.png")).convert("RGB")
    banner = Image.open(os.path.join(ART, "banner.png")).convert("RGB")

    # 1) WizardImageFile — fit the WHOLE poster into the 164:314 slot (2x = 328x628) so the
    #    logo AND the wide «РУСИФИКАТОР» plaque stay intact; letterbox filled with a blurred cover.
    wiz = fit_blur(poster, 328, 628)
    wiz.save(os.path.join(ART, "wizard-image.bmp"))

    # 2) Wide header from the banner (kept for an optional full-width Welcome header).
    banner.resize((994, round(994 * banner.size[1] / banner.size[0])), Image.LANCZOS) \
          .save(os.path.join(ART, "banner-wide.bmp"))

    # 3) Icon — square crop around Marco, multi-size .ico.
    marco = square_frac(poster, cx=0.47, cy=0.68, half=0.17).resize((256, 256), Image.LANCZOS)
    marco.save(os.path.join(ART, "mst-ru.ico"),
               sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])

    # 3b) Small wizard image (top-right corner of the interior pages).
    marco.resize((138, 140), Image.LANCZOS).save(os.path.join(ART, "wizard-small.bmp"))

    # ---- preview mocks (for review only) ----
    _preview_welcome(wiz)
    _preview_icon(marco)
    print("wrote:", ", ".join(sorted(f for f in os.listdir(ART)
                                     if f.endswith((".bmp", ".ico", ".png")) and f != "poster.png"
                                     and f != "banner.png")))


def _preview_welcome(wiz):
    S = 2                                   # 2x for a crisp mock
    W, H, IMG_W, PAGE_H = 497, 360, 164, 312
    c = Image.new("RGB", (W * S, H * S), "white")
    d = ImageDraw.Draw(c)
    c.paste(wiz.resize((IMG_W * S, PAGE_H * S), Image.LANCZOS), (0, 0))
    tx = (IMG_W + 18) * S
    d.text((tx, 24 * S), "Welcome to the Metal Slug Tactics", font=_font(True, 15 * S), fill=(0, 0, 0))
    d.text((tx, 44 * S), "Russian translation Setup", font=_font(True, 15 * S), fill=(0, 0, 0))
    body = ["This will install the Russian translation for",
            "Metal Slug Tactics on your computer.",
            "",
            "It finds your copy of the game, rebuilds the",
            "text and fonts from it, and switches the game",
            "to Russian. No game files are downloaded.",
            "",
            "Close the game, then click Next to continue."]
    for i, line in enumerate(body):
        d.text((tx, (86 + i * 20) * S), line, font=_font(False, 12 * S), fill=(30, 30, 30))
    d.rectangle((0, PAGE_H * S, W * S, H * S), fill=(240, 240, 240))
    d.line((0, PAGE_H * S, W * S, PAGE_H * S), fill=(200, 200, 200), width=S)
    for label, x in (("Next >", 372), ("Cancel", 430)):
        d.rectangle((x * S, (PAGE_H + 16) * S, (x + 55) * S, (PAGE_H + 34) * S),
                    outline=(140, 140, 140), width=S, fill=(250, 250, 250))
        d.text(((x + 12) * S, (PAGE_H + 20) * S), label, font=_font(False, 11 * S), fill=(0, 0, 0))
    c.save(os.path.join(ART, "preview-welcome.png"))


def _preview_icon(marco):
    sizes = [16, 24, 32, 48, 64, 128, 256]
    pad, gap = 20, 20
    W = pad * 2 + sum(sizes) + gap * (len(sizes) - 1)
    H = 256 + pad * 2 + 24
    c = Image.new("RGB", (W, H), (230, 230, 230))
    d = ImageDraw.Draw(c)
    x = pad
    for s in sizes:
        ic = marco.resize((s, s), Image.LANCZOS)
        c.paste(ic, (x, pad + (256 - s)))
        d.text((x, pad + 256 + 4), f"{s}px", font=_font(False, 12), fill=(60, 60, 60))
        x += s + gap
    c.save(os.path.join(ART, "preview-icon.png"))


if __name__ == "__main__":
    main()
