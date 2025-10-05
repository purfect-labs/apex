# Minimal PyInstaller spec file for APEX debugging
# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Simple path setup
current_dir = Path.cwd()
if current_dir.name == 'build':
    root_dir = current_dir.parent.parent
else:
    root_dir = current_dir.parent.parent
app_dir = root_dir / 'native' / 'app'

print(f"DEBUG: Building from {app_dir / 'apex_app.py'}")
print(f"DEBUG: File exists: {(app_dir / 'apex_app.py').exists()}")

# Minimal Analysis
a = Analysis(
    [str(app_dir / 'apex_app.py')],
    pathex=[str(app_dir), str(root_dir)],
    binaries=[],
    datas=[],
    hiddenimports=[
        'fastapi',
        'uvicorn', 
        'webview',
        'cryptography.fernet',
        'keyring'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Create as onefile instead of onedir
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='APEX',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Enable console for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)