
# -*- mode: python ; coding: utf-8 -*-
a = Analysis(
    ['apex_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('web', 'web'),
        ('config', 'config'),
    ],
    hiddenimports=[
        'webview',
        'uvicorn', 
        'fastapi',
        'websockets',
        'pydantic',
        'yaml',
        'keyring',
        'cryptography',
        'psutil',
        'jinja2',
        'aiofiles',
    ],
    hookspath=[],
    hooksconfig={},
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
    name='apex-macos',
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
)
