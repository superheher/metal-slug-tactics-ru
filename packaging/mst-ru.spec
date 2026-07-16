# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller: the standalone translator installer (a single file).

Builds dist/mst-ru-setup(.exe). It bundles ONLY the translation and font sources
(translation/, font/) plus UnityPy's data (the Unity type database, without which the
bundles cannot be read). The game's assets are not here — the patch is built on the player's machine.

Run from the repository root:  pyinstaller packaging/mst-ru.spec
"""
import os
from PyInstaller.utils.hooks import collect_all

# SPECPATH — the folder of this spec (packaging/); the repository root is one level up.
ROOT = os.path.dirname(SPECPATH)

datas = [(os.path.join(ROOT, 'translation'), 'translation'),
         (os.path.join(ROOT, 'font'), 'font')]
binaries = []
hiddenimports = ['paths', 'extract', 'validate', 'build', 'spritefont']

# UnityPy drags along native decoders and their data: the Unity type database, the
# fmod_toolkit audio bridge (libfmod), the texture decoders (astc_encoder/texture2ddecoder/etcpak)
# and archspec with its JSON description of processors. Without them the binary crashes reading a bundle.
# We collect the packages that are actually installed on this platform.
for _pkg in ('UnityPy', 'fmod_toolkit', 'astc_encoder', 'archspec',
             'texture2ddecoder', 'etcpak'):
    try:
        _d, _b, _h = collect_all(_pkg)
    except Exception:
        continue
    datas += _d
    binaries += _b
    hiddenimports += _h

a = Analysis(
    [os.path.join(ROOT, 'tools', 'install.py')],
    pathex=[os.path.join(ROOT, 'tools')],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
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
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
