"""
LibHandler.py
Shared library loader, handles loading the correct library for
whatever system
"""

from ctypes import *
import os
import sys

def GetSharedLibrary():
    # Determine platform
    plat = sys.platform
    if plat == "win32":
        # get windows path
        libPath = os.getenv('APPDATA')
        libPath += "\\krita\\pykrita\\ChromaticAberration\\ChromaticAberration_WIN"
    elif plat == "darwin":
        # get osx path
        # TODO: check if this will work...
        libPath = os.getenv('HOME')
        libPath += "/Library/Application Support/Krita/pykrita/ChromaticAberration/ChromaticAberration_MAC"
    else:
        # get linux path
        libPath = os.getenv('HOME')
        libPath += "/.local/share/krita/pykrita/ChromaticAberration/ChromaticAberration_NIX"
    # Determine 32 or 64 bit
    if sys.maxsize < 2**32:
        libPath += "32.so"
    else:
        libPath += "64.so"
    # Load and set argtypes
    dll = CDLL(libPath)
    
    return dll
