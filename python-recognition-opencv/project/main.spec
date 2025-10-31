# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('.venv\\Lib\\site-packages\\kivy\\data', 'kivy_install\\data'), ('.venv\\Lib\\site-packages\\cv2\\data', 'cv2\\data'), ('..\\..\\faces', 'faces'), ('..\\..\\cadastros', 'cadastros'), ('..\\..\\pasta_usuarios', 'pasta_usuarios'), ('..\\..\\lib', 'lib')],
    hiddenimports=['kivy.weakmethod', 'numpy', 'cv2'],
    hookspath=['hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
