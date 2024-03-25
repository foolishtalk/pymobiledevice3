# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata

datas = []
datas += copy_metadata('pyimg4')


a = Analysis(
    ['../pymobiledevice3/__main__.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['ipsw_parser', 'zeroconf', 'pyimg4', 'zeroconf._utils.ipaddress', 'zeroconf._handlers.answers'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['gpxpy', 'pygments', 'termcolor', 'coloredlogs', 'inquirer3', 'IPython', 'hexdump', 'pycrashreport', 'pyreadline3'],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='pydevice',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity='Developer ID Application: Ye Kun Zhang (J3BJ7G2PUN)',
    entitlements_file='./pymobile.entitlements',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='pydevice',
)
