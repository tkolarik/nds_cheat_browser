# NDS_Cheat_Browser_GUI.spec
a = Analysis(
    ['gui/cheat_browser.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('utils', 'utils'),  # Include utils module
    ],
    hiddenimports=[
        'tkinter',
        'utils',
        'utils.cheat_utils',
        'utils.generate_gameid',
        'utils.header_crc32'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

# Create data directory in the executable
a.datas += [('data/cheats.xml', '', 'DATA')]

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='NDS_Cheat_Browser_GUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['static/icons/gui.ico'],
)