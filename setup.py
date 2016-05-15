import sys
from cx_Freeze import setup, Executable

build_exe_options = {"build_exe":"../build/",
                     "include_files":["./icons/"],
                     "includes":["tkinter.font"]}

base = None
if sys.platform == 'win32':
    base = "Win32GUI"
##################################################### Does this work on win64?

setup(  name="OSC Video Timer",
        version="0.1",
        description="Gets the time on a video from CasparCG using the OSC Protocol, made by Ben",
        options={"build_exe": build_exe_options},
        executables = [Executable("osc_videotimer.py", base=base)])
