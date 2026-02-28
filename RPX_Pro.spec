# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file fuer RPX Pro
# Build: pyinstaller RPX_Pro.spec --clean --noconfirm

block_cipher = None

a = Analysis(
    ['RPX_Pro_1.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('rulesets', 'rulesets'),
    ],
    hiddenimports=[
        'PySide6.QtMultimedia',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'scipy', 'PIL'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='RPX_Pro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='RPX_Pro',
)
