<p align="center"><img src="assets/banner.jpg" alt="Metal Slug Tactics — Russian translation" width="900"></p>

[Русский](README.md) · **English**

# Metal Slug Tactics — Russian translation

A full translation: **5273 strings, ~280k characters** — the entire game, including the campaign
dialogue. It works as a **native locale**: Russian is added to the game itself as a separate
language. No BepInEx, no Google Translate, no on-the-fly text interception. Nothing is sent to the
network.

Built for game version **1.0.4**, for the **Windows** version of the game (the only PC platform it
ships on). Linux/macOS players run that same Windows build via Proton/Wine.

> The translation is built from **your** copy of the game, on your own machine. The game's assets
> are not here and are not sent anywhere — see [Assets and copyright](#assets-and-copyright).

<p align="center"><img src="assets/screenshot-pixel-font.jpg" alt="The in-game «РАЗМЕСТИТЕ СОЛДАТ» caption" width="820"></p>
<p align="center"><em>The banner captions are a sprite pixel font, not text — the Cyrillic is redrawn in the game's native style.</em></p>

---

## Installation

### Easy — the ready-made installer (no Python, no dependencies)

1. Download **`mst-ru-setup.exe`** from the [**Releases**](../../releases/latest) page. It is a
   self-contained Windows installer — nothing else has to be installed (no Python, no .NET).
2. **Close the game** and double-click the installer. If SmartScreen shows “Windows protected your
   PC / unknown publisher”, click **“More info” → “Run anyway”** (the installer is not code-signed).
3. Click through the wizard and let it run — it finds the game, builds the translation from your copy
   and enables Russian.
4. Launch the game — the language is already Russian.

A Start-menu shortcut **“Install / update the Russian translation”** is added; run it again after
every Steam update of the game. There is also a **“Revert to English”** shortcut.

### From source (needs Python 3)

```sh
# Windows
install.bat

# Linux and macOS
./install.sh
```

The wrapper sets up a virtual environment, installs the dependencies, builds and installs the translation.

The game path is found automatically — by Steam libraries and common Wine prefixes.
If it is not found, set it explicitly:

```sh
# Windows
set MST_PATH=C:\path\to\steamapps\common\MST
install.bat

# Linux and macOS
MST_PATH="/path/to/steamapps/common/MST" ./install.sh
```

### After a game update

**After every Steam update — install the translation again.** An update restores the native
bundles; the installer notices this, refreshes the backup and rebuilds the translation from the new original.

### Rollback

```sh
./mst-ru-setup-...   --revert      # the ready-made installer
./install.sh --revert              # from source (install.bat --revert on Windows)
```

Restores the originals from the backup. Then choose English in **НАСТРОЙКИ → Язык**.

### Checking without installing

`--dry-run` builds and checks the translation, but does not touch the game — handy after edits.

---

## What is here

```
translation/ru.json              the translation: string id -> Russian text
font/tmp_metalslug_7x7.json      22 Cyrillic letters for the TMP font (7×7 grid)
font/sprite_banner_25x25.json     8 Cyrillic letters for the sprite font (25×25 grid)
glossary/                        the term glossary and the canon for labels inside placeholders
tools/                           game discovery, extraction, validation, build, install
packaging/mst-ru.spec / .iss     build the standalone Windows installer (PyInstaller + Inno Setup)
packaging/art/                   installer branding (poster, icon)
.github/workflows/               CI: build the Windows installer, publish the rolling latest release
```

---

## Assets and copyright

**The game's assets are not here and never will be.** The game, its original text, fonts and graphics
belong to **SNK, Dotemu and Leikir Studio**. This is an unofficial, non-commercial fan translation,
in no way affiliated with the rights holders.

The localized bundles are **not distributed**: they are built on the player's machine from their own
copy of the game (Steam appid `1590760`). The `backup/` and `build/` folders never end up in git.
Use the translation only with a legally purchased copy of Metal Slug Tactics.

The code and translation sources are under [MIT](LICENSE).

---

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

---

## How to edit the translation

1. Open `translation/ru.json` — a flat dictionary `"string id": "Russian text"`.
2. Edit the text. **Do not touch** the paths inside `{...}` or the tags `<...>` — the output will
   break. But the text AFTER the colon inside a placeholder (`{Move:перемещает}`) is exactly what the
   player sees, so it can and should be edited.
3. `./install.sh` (or `install.bat`) — checks the markup integrity, rebuilds and installs.
   Want to only check — add `--dry-run`.

## How to edit the letters

The shapes live in `font/` as plain text: `#` is ink, `.` is empty.
Edit the grid — the installer rebuilds. The outline, shadow, border and the gradient with
dithering are added automatically by the recipe.

## Term decisions

- Peregrine Falcons / Falcons → **«Сапсаны»** · SPARROWS → **«Воробьи»**
- unit → **боец** · Sync → **синхроудар** · World Government → **Всемирное правительство**
- `HP`, `DMG`, `ADR`, `XP`, `Init` stay in Latin — these are labels in cramped UI spots.
- `WASD` stays `WASD` (the old fan translation had «Ц/Ф/Ы/В» — the keys are physically the same, after all).

Details are in `glossary/`.

---

## Building the installer (for maintainers)

On **Windows**, with [Inno Setup 6](https://jrsoftware.org/isdl.php) installed:

```sh
pip install UnityPy numpy Pillow pyinstaller
python packaging/make_wizard_images.py   # only after changing the art in packaging/art/
pyinstaller packaging/mst-ru.spec        # -> dist/mst-ru/ (self-contained one-folder bundle)
iscc packaging/mst-ru.iss                # -> dist/mst-ru-setup.exe
```

PyInstaller produces the bundle; Inno Setup wraps it into a single `mst-ru-setup.exe`. CI
(`.github/workflows/build-installers.yml`) does both on a Windows runner and publishes the exe as a
single rolling **latest** release, named with the build date. To trigger a build, push a version
tag or run the workflow from the Actions tab:

```sh
git tag v1.0.4
git push origin v1.0.4
```
