# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller: the Windows patcher as a single self-contained exe (onefile, windowed).

Produces dist/mst-ru-setup.exe. Double-clicking it opens a small window (game folder +
Install), unpacks to a temp folder, rebuilds the translation from the player's own copy,
enables Russian, then cleans up — no install, nothing left behind.

The exe carries ONLY the translation and font sources (translation/, font/) plus
UnityPy's data (the Unity type database). The game's assets are not here.

Run from the repository root:  pyinstaller packaging/mst-ru.spec
"""
import os
from PyInstaller.utils.hooks import collect_all

# SPECPATH — the folder of this spec (packaging/); the repository root is one level up.
ROOT = os.path.dirname(SPECPATH)
ICON = os.path.join(SPECPATH, 'art', 'mst-ru.ico')   # applied only on Windows builds

datas = [(os.path.join(ROOT, 'translation'), 'translation'),
         (os.path.join(ROOT, 'font'), 'font'),
         (os.path.join(SPECPATH, 'art', 'poster.jpg'), 'art'),   # shown in the GUI window
         (os.path.join(SPECPATH, 'art', 'mst-ru.ico'), 'art'),   # exe icon
         (os.path.join(SPECPATH, 'art', 'mst-ru.png'), 'art'),   # window/taskbar icon (iconphoto)
         (os.path.join(SPECPATH, 'art', 'JetBrainsMonoNL-Regular.ttf'), 'art'),  # log/link font
         (os.path.join(SPECPATH, 'art', 'JetBrainsMono-OFL.txt'), 'art')]        # its license
_build_date = os.path.join(ROOT, 'build_date.txt')   # written by CI; shown by the patcher
if os.path.exists(_build_date):
    datas.append((_build_date, '.'))
binaries = []
hiddenimports = ['paths', 'install', 'extract', 'validate', 'build', 'spritefont',
                 'darkdetect', 'sv_ttk']

# UnityPy drags along native decoders and their data: the Unity type database, the
# fmod_toolkit audio bridge (libfmod), the texture decoders (astc_encoder/texture2ddecoder/etcpak)
# and archspec with its JSON description of processors. Without them the binary crashes reading a bundle.
# We collect the packages that are actually installed on this platform.
for _pkg in ('UnityPy', 'astc_encoder', 'archspec',
             'texture2ddecoder', 'etcpak', 'sv_ttk'):
    try:
        _d, _b, _h = collect_all(_pkg)
    except Exception:
        continue
    datas += _d
    binaries += _b
    hiddenimports += _h

a = Analysis(
    [os.path.join(ROOT, 'tools', 'gui.py')],
    pathex=[os.path.join(ROOT, 'tools')],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=['fmod_toolkit'],   # UnityPy's audio decoder — we never touch audio (~2-4 MB)
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='mst-ru-setup',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=(ICON if os.name == 'nt' else None),
)
