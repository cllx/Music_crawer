import sys
#from cx_Freeze import setup,Executable
from cx_Freeze import *
import os
#这里面的tcl和tk文件路径一般在本机安装的Python目录下面，由于我这里是安装了anaconda，所以就在anaconda目录下面了
#以及下面的路径，都很重要，如果写错了会打包失败
os.environ['TCL_LIBRARY'] = r'E:\Anaconda3\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'E:\Anaconda3\tcl\tk8.6'

include_files = [
    r'E:\Anaconda3\DLLs\tcl86t.dll',
    r'E:\Anaconda3\DLLs\tk86t.dll'
]

build_exe_options = {"packages": ["os", "tkinter"], "include_files": include_files}

base = None
if sys.platform == "win32":
    base = "Win32GUI"
setup(
    name=" wangyiyun_music",
    version="2.0",
    description="cloud Music",
    options={"build_exe": build_exe_options},
    executables=[Executable("wangyiyun_music2.py", base=base)]
)
