# PyInstaller spec file for APEX Native macOS Application
# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Add paths for source files - handle both packaging and build directory execution
current_dir = Path.cwd()
if current_dir.name == 'build':
    # Running from build directory
    root_dir = current_dir.parent.parent
else:
    # Running from packaging directory
    root_dir = current_dir.parent.parent
app_dir = root_dir / 'native' / 'app'

# Debug output
print(f"APEX Build Debug:")
print(f"  Current dir: {current_dir}")
print(f"  Root dir: {root_dir}")
print(f"  App dir: {app_dir}")
print(f"  App dir exists: {app_dir.exists()}")
print(f"  apex_app.py exists: {(app_dir / 'apex_app.py').exists()}")

sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(app_dir))
sys.path.insert(0, str(root_dir))

# Import to get hidden imports
try:
    import webview
    import uvicorn
    import fastapi
    import cryptography
    import keyring
except ImportError as e:
    print(f"Warning: Could not import {e.name}")

# Define application info
APP_NAME = 'APEX'
APP_VERSION = '3.0.0'
APP_BUNDLE_ID = 'com.apex.commandcenter'
APP_COPYRIGHT = 'Copyright © 2024 APEX. All rights reserved.'

# Hidden imports needed for PyInstaller
hidden_imports = [
    # FastAPI and Uvicorn
    'fastapi',
    'fastapi.middleware',
    'fastapi.middleware.cors',
    'fastapi.responses',
    'fastapi.staticfiles',
    'uvicorn',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    
    # WebView
    'webview',
    'webview.platforms',
    'webview.platforms.cocoa',
    
    # Cryptography and licensing
    'cryptography',
    'cryptography.fernet',
    'cryptography.hazmat',
    'cryptography.hazmat.primitives',
    'cryptography.hazmat.primitives.kdf',
    'cryptography.hazmat.primitives.kdf.pbkdf2',
    'cryptography.hazmat.primitives.hashes',
    'keyring',
    'keyring.backends',
    'keyring.backends.macOS',
    
    # Other dependencies
    'pydantic',
    'pydantic.v1',
    'yaml',
    'websockets',
    'websockets.server',
    'websockets.client',
    'psutil',
    'requests',
    'subprocess',
    'platform',
    'socket',
    'uuid',
    'json',
    'base64',
    'gzip',
    'mimetypes',
    'logging',
    'threading',
    'asyncio',
    'signal',
    'time',
    'webbrowser',
]

# Data files to include (relative to root directory) - only existing dirs
datas = []

# Add data files only if they exist
data_paths = [
    ('web/templates', 'web/templates'),
    ('web/static', 'web/static'), 
    ('web/public', 'web/public'),
    ('config', 'config'),
]

for src_path, dst_path in data_paths:
    full_src_path = root_dir / src_path
    if full_src_path.exists():
        datas.append((str(full_src_path), dst_path))

# Binary files to include (if any)
binaries = []

# Collect all Python files
a = Analysis(
    [str(app_dir / 'apex_app.py')],
    pathex=[str(current_dir), str(app_dir), str(root_dir)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'PIL',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
        'jupyter',
        'IPython',
        'sphinx',
        'pytest',
        'setuptools',
        'distutils',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
    optimize=2,  # Enable optimization
)

# Remove duplicate entries
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Create executable in onedir mode (exclude_binaries=True forces onedir)
exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,  # This explicitly forces onedir mode
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(root_dir / 'assets' / 'icon.icns') if (root_dir / 'assets' / 'icon.icns').exists() else None,
)

# Create COLLECT for onedir distribution
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name=APP_NAME
)

# Create macOS app bundle from COLLECT
app = BUNDLE(
    coll,
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    name=f'{APP_NAME}.app',
    icon=str(root_dir / 'assets' / 'icon.icns') if (root_dir / 'assets' / 'icon.icns').exists() else None,
    bundle_identifier=APP_BUNDLE_ID,
    version=APP_VERSION,
    info_plist={
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': 'APEX Command Center',
        'CFBundleIdentifier': APP_BUNDLE_ID,
        'CFBundleVersion': APP_VERSION,
        'CFBundleShortVersionString': APP_VERSION,
        'CFBundlePackageType': 'APPL',
        'CFBundleSignature': 'apex',
        'CFBundleExecutable': APP_NAME,
        'CFBundleIconFile': 'icon.icns',
        'NSHumanReadableCopyright': APP_COPYRIGHT,
        'NSHighResolutionCapable': True,
        'NSSupportsAutomaticGraphicsSwitching': True,
        'NSAppTransportSecurity': {
            'NSAllowsArbitraryLoads': True,  # Allow localhost connections
            'NSExceptionDomains': {
                'localhost': {
                    'NSExceptionAllowsInsecureHTTPLoads': True,
                    'NSExceptionMinimumTLSVersion': '1.0',
                    'NSExceptionRequiresForwardSecrecy': False,
                },
                '127.0.0.1': {
                    'NSExceptionAllowsInsecureHTTPLoads': True,
                    'NSExceptionMinimumTLSVersion': '1.0',
                    'NSExceptionRequiresForwardSecrecy': False,
                }
            }
        },
        'NSRequiresAquaSystemAppearance': False,
        'LSApplicationCategoryType': 'public.app-category.developer-tools',
        'LSMinimumSystemVersion': '10.14',  # Minimum macOS version
        'CFBundleDocumentTypes': [],
        'UTExportedTypeDeclarations': [],
        'UTImportedTypeDeclarations': [],
    },
)