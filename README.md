# Metal Slug Tactics — Russian translation

A full translation: **5273 strings, 280k characters** — the entire game, including the
campaign dialogue. It works as a **native locale**: Russian is added to the game itself as a
separate language. No BepInEx, no Google Translate, no on-the-fly text interception. Nothing
is sent to the network.

Built for game version **1.0.4**, macOS + Whisky (Wine).

For comparison, the only existing fan pack covers **2518 strings** — less than half the game,
with no campaign dialogue at all, and everything unfamiliar it machine-translates through
Google on the fly, sending both the game's text and the player's nickname there.

## How to install

```sh
./install.sh
```

The script creates the environment itself, extracts the originals from your copy of the game,
checks the translation, builds the bundles, installs them and enables Russian.

**After every Steam update of the game — run it again.** An update restores the native
bundles; the script notices this, refreshes the backup and rebuilds the translation from the
new original.

The game path is found automatically. If it is not — set it explicitly:
```sh
MST_PATH="/path/to/steamapps/common/MST" ./install.sh
```

## What is here

```
translation/ru.json              the translation: string id -> Russian text
font/tmp_metalslug_7x7.json      22 Cyrillic letters for the TMP font (7×7 grid)
font/sprite_banner_25x25.json     8 Cyrillic letters for the sprite font (25×25 grid)
glossary/                        the term glossary and the canon for labels inside placeholders
tools/                           extraction, validation, build
```

**The game's assets are not here and never will be.** They belong to SNK, Dotemu and Leikir
Studio, weigh close to a hundred megabytes and go stale with every patch. The bundles are built
from your own copy of the game; the `backup/` and `build/` folders never end up in git.

## How it works

### Text

The game has its own localization system (Unity Localization) with nine languages; Russian is
not among them, and a tenth cannot be added. So Russian took over the slot of **Brazilian
Portuguese** — a language you almost certainly do not need. English and all the rest are left
untouched: in the `НАСТРОЙКИ → Язык` menu a «Русский» item appears, and you can switch between
it and English.

The key thing that made the swap possible: the Addressables catalog **stores no bundle
checksums**, so the string table can be rebuilt and the game will not notice.

Three non-obvious facts, learned the hard way:

- `Save/Options` → `Locale.option` takes the **locale's asset name**, not a code:
  `"Portuguese (Brazil) (pt-BR)"`, not `"pt-BR"`. With a code the game silently ignores the setting.
- The language name in the list is taken from the `UI/240000458967474176` string inside **the
  table itself** (in the English one it is `English`), not from the locale object's `m_LocaleName`
  field — the game does not read that.
- The `UI/167188675005767680` string = `{Platform.IsConsole:{Locale}|System ({Locale})}` labels
  the system-language item. In the Russian table it is replaced with `{Locale}`, otherwise the
  item is called «Системный (Русский)».

### Banner captions — a separate story

The big captions on the black bar — `ХОД ИГРОКА`, `ХОД ПРОТИВНИКА`, `РАЗМЕСТИТЕ БОЙЦОВ`,
`ПОБЕДА`, `ПОРАЖЕНИЕ` — are drawn **not as text but as sprites**: the `SpriteText` component
splits a string into characters and pulls a separate 25×25 image for each one from the
`SpriteFont` table. There were no Cyrillic codes there — hence an empty black bar instead of a
caption. Editing the TextMeshPro fonts is useless here in principle.

Only five captions are drawn with sprites, and English needs only the letters
`A C D E F I L M N O P R S T U V Y` in them. That means `G J Q W Z !` and the digits sit in the
set as dead weight — their pixels are the ones repainted for Cyrillic. English stays fully intact.

- **12 letters** (`А В Е К М Н О Р С Т Х`, and also `З` → the digit `3`) **reference Latin sprites** —
  the shapes coincide, not a single pixel is touched.
- **8 letters** (`Б Г Д Ж И Й П Ц`) are redrawn from scratch. `И` is a mirrored `N`, reflected pixel for pixel.

The letter recipe is reverse-engineered from the originals and reproduces `H`, `T`, `E`, `F` **pixel for pixel**:

- fill — five gradient bands of two rows each: `(248,208,48) → (248,144,24) → (248,104,0) → (240,48,0) → (176,0,0)`;
- between the bands — **dithering**: two rows of a checkerboard, dark colour when `(row + column)` is even;
- shadow `(120,0,0)` — along the **top and left** edge of the fill, not a ring;
- white outline `(248,248,248)` — 1px outward;
- black border — a ring around the outline **plus** a drop shadow offset down-right.

## How to edit the translation

1. Open `translation/ru.json` — a flat dictionary `"string id": "Russian text"`.
2. Edit the text. **Do not touch** the paths inside `{...}` or the tags `<...>` — the output
   will break. But the text AFTER the colon inside a placeholder (`{Move:перемещает}`) is exactly
   what the player sees, so it can and should be edited.
3. `./install.sh` — checks the markup integrity, rebuilds and installs.

## How to edit the letters

The shapes live in `font/` as plain text: `#` is ink, `.` is empty.
Edit the grid — `./install.sh` rebuilds. The outline, shadow, border and the gradient with
dithering are added automatically by the recipe.

## Term decisions

- Peregrine Falcons / Falcons → **«Сапсаны»** · SPARROWS → **«Воробьи»**
- unit → **боец** · Sync → **синхроудар** · World Government → **Всемирное правительство**
- `HP`, `DMG`, `ADR`, `XP`, `Init` stay in Latin — these are labels in cramped UI spots.
- `WASD` stays `WASD` (the old fan translation had «Ц/Ф/Ы/В» — the keys are physically the same, after all).

Details are in `glossary/`.

## Rollback

```sh
cp backup/*.bundle "<game>/Metal Slug Tactics_Data/StreamingAssets/aa/StandaloneWindows64/"
```
And choose English in the game's settings.
