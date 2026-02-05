# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for DIAS Package Creator.
Creates a single-file executable for the GUI application.

To build:
    pyinstaller build_exe.spec

Or use the shorthand:
    pyinstaller --onefile --windowed app.py
"""

import sys
from pathlib import Path

block_cipher = None

# Get the absolute path to the project root
project_root = Path(SPECPATH).resolve()

# Data files to include (XSD schemas, config examples, etc.)
datas = [
    (str(project_root / 'dias_mets.xsd'), '.'),
    (str(project_root / 'dias_premis.xsd'), '.'),
    (str(project_root / 'submissionDescription.xsd'), '.'),
    (str(project_root / '.env.example'), '.'),
    (str(project_root / 'dias_config.example.yml'), '.'),
]

# Hidden imports that PyInstaller might miss
hiddenimports = [
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'xml.etree.ElementTree',
    'hashlib',
    'mimetypes',
    'uuid',
    'threading',
    'queue',
    'concurrent.futures',
    'yaml',  # For config loading
    'ctypes',  # For Windows memory info
    'ctypes.wintypes',
]

a = Analysis(
    ['app.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'cv2',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='dias-package-creator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if available: 'assets/icon.ico'
)

# For macOS, create an app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='DIAS Package Creator.app',
        icon=None,  # Add icon path here if available: 'assets/icon.icns'
        bundle_identifier='com.dias.package-creator',
        info_plist={
            'CFBundleName': 'DIAS Package Creator',
            'CFBundleDisplayName': 'DIAS Package Creator',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'NSHighResolutionCapable': True,
        },
    )
