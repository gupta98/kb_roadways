import sys
import os
from cx_Freeze import setup, Executable

#FILES
files = [
    ".\\__Assets\\",
    ".\\__Database\\",
    ".\\__Files\\",
    ".\\__GUIs\\",
]

#TARGET
target = Executable(
    script = "main.py",
    base = "WIN32GUI",
    icon = ".\\__Assets\\Logos\\CompanyLogo.png"
)

#SETUP
setup(
    name = "K.B. Roadways Business Tracking System",
    version = "1.0",
    description = "",
    author = "Debtanu Gupta",
    options = {"build_exe" : {"include_files": files}},
    executables = [target]
)