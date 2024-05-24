# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

datas = []
datas += collect_data_files('tkinterdnd2')
a = Analysis(['oneroster_csv_converter.py'],
             pathex=[],
             binaries=[],
             datas=datas,
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

a.datas += [('resources\\logo_120X120.png', 'resources\\logo_120X120.png', 'DATA'),
            ('resources\\invalidErrorConfig.json', 'resources\\invalidErrorConfig.json', 'DATA'),
]
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
Key = ['mkl']

def remove_from_list(input, keys):
    outlist = []
    for item in input:
        name, _, _ = item
        flag = 0
        for key_word in keys:
            if name.find(key_word) > -1:
                flag = 1
        if flag != 1:
            outlist.append(item)
    return outlist

a.binaries = remove_from_list(a.binaries, Key)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,  
          [],
          name='oneroster_csv_converter',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )