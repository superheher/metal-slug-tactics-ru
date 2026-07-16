#!/usr/bin/env python3
"""Checks the translation for what matters to the ENGINE, without nitpicking what matters to the player.

What is checked:
  • placeholder paths (including nested ones) and SmartFormat's service constructs;
  • markup tags;
  • line breaks;
  • English remnants in the Russian text.

What is NOT counted as an error:
  • translating the label text INSIDE a placeholder ({Move:перемещает}) — the player sees it;
  • a dropped placeholder, if it was a purely English construct.
    Example: {Frags} frag{Frags:p:|s} -> «Фрагов: {Frags}». The English construct gives
    two forms (frag/frags), Russian needs three, and the genitive case works for any
    number. The extra placeholder simply is not substituted — the engine does not care.

FATAL (the build will not run):
  • no translation;
  • the translation INVENTED a placeholder that is not in the original — the engine will not substitute it;
  • broken tags.
"""
import collections
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

NUMFMT = {"Delay", "FPS", "RemainingTime"}          # {Delay:0.#} — a number format, not text
TAG = re.compile(r'</?[A-Za-z][^<>]*>')             # a tag, not a condition like <1?
STRIP = re.compile(r'\{(?:[^{}]|\{[^{}]*\})*\}|<[^<>]+>')
KEEP_LATIN = {"Metal", "Slug", "Tactics", "Steam", "Discord", "Leikir", "English",
              "SNK", "Dotemu", "WASD", "Studio", "Enter", "Init"}
SKIP_TABLES = {"Test StringTable"}                  # debug strings, the player does not see them


def top_placeholders(s):
    out, depth, start = [], 0, None
    for i, c in enumerate(s):
        if c == "{":
            if depth == 0:
                start = i
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0 and start is not None:
                out.append(s[start:i + 1])
                start = None
    return out


def skeleton(s):
    """Everything that must survive: paths (including nested) and the service constructs."""
    sk = []
    for p in top_placeholders(s):
        inner = p[1:-1]
        path = inner.split(":", 1)[0].strip()
        sk.append(path)
        if path in NUMFMT:
            sk.append(inner)                        # the number format must match in full
        for kw in ("cond:", "choose("):
            if kw in inner:
                sk.append(kw)
        sk += skeleton(inner)                       # recurse into nested placeholders
    return sk


def main():
    en_path = paths.build("en_strings.json")
    if not os.path.exists(en_path):
        sys.exit("✗ No build/en_strings.json — run tools/extract.py first")

    tables = json.load(open(en_path))["tables"]
    en, table_of = {}, {}
    for name, rows in tables.items():
        for i, v in rows.items():
            en[str(i)] = v
            table_of[str(i)] = name.replace("_en-US", "")
    ru = json.load(open(paths.res("translation", "ru.json")))

    fatal = collections.defaultdict(list)
    warn = collections.defaultdict(list)

    for i, e in en.items():
        t = ru.get(i)
        if not t or not t.strip():
            fatal["no translation"].append(i)
            continue

        se, st = collections.Counter(skeleton(e)), collections.Counter(skeleton(t))
        invented = st - se
        dropped = se - st
        if invented:
            fatal["invented placeholder"].append(f"{i}: extra {dict(invented)} | {t[:40]!r}")
        elif dropped:
            warn["dropped placeholder"].append(f"{i}: {e[:38]!r} -> {t[:38]!r}")

        if collections.Counter(TAG.findall(e)) != collections.Counter(TAG.findall(t)):
            fatal["broken tags"].append(f"{i}: {e[:45]!r}")
        if e.count("\n") != t.count("\n"):
            warn["line breaks"].append(i)

    for i, t in ru.items():
        if table_of.get(i) in SKIP_TABLES:
            continue
        left = [w for w in re.findall(r"\b[A-Za-z][a-z]{3,}\b", STRIP.sub(" ", t))
                if w not in KEEP_LATIN]
        if left:
            warn["English remnant"].append(f"{i}: {left} | {t[:45]!r}")

    print(f"strings in the game: {len(en)}   translated: {len(ru)}")

    for kind, items in warn.items():
        print(f"\n  ~ {kind}: {len(items)}  (acceptable)")
        for x in items[:3]:
            print(f"      {x}")
    for kind, items in fatal.items():
        print(f"\n  ✗ {kind}: {len(items)}  (FATAL)")
        for x in items[:5]:
            print(f"      {x}")

    if fatal:
        print("\n  ✗ build not possible")
        return 1
    print("\n  ✓ no fatal errors")
    return 0


if __name__ == "__main__":
    sys.exit(main())
