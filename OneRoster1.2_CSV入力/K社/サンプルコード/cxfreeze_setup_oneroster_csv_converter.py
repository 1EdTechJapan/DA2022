# coding: utf-8
# cx_Freeze 用セットアップファイル

from distutils.command.bdist import bdist
import sys
from cx_Freeze import setup, Executable
import os 

base = None
#includefiles = []
build_exe_options = {"packages":["pandas", "numpy", "pandera"],
                    "includes":["tkinter", "tkinterdnd2"],
                    "include_files":[(os.path.join('resources','logo_120X120.png'), os.path.join('resources','logo_120X120.png')),
                                     ('invalidErrorConfig.json', 'invalidErrorConfig.json')
                                     ],
                    "excludes": ["PyQt4","PyQt5"],
}
bdist_msi_options = {
    "upgrade_code": "{90B20E18-A41E-49F9-B382-5168E4A481F5}"
    }
if sys.platform == 'win32' : base = 'Win32GUI'
exe = Executable(script = 'oneroster_csv_converter.py',
                 base = base, 
                 shortcutName="oneroster_csv_converter",
                 shortcutDir="DesktopFolder")
 
setup(name = 'oneroster_csv_converter',
      version = '0.6',
      options = {'build_exe':build_exe_options,
                 'bdist_msi':bdist_msi_options,
      },
      description = 'oneroster_csv_converter',
      executables = [exe])