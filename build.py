import os
import platform

import ddddocr

separator = ";"
if platform.system() != "Windows":
    separator = ":"

dir_path = os.path.dirname(ddddocr.__file__)
onnx_name = "common_old.onnx"
onnx_path = os.path.join(dir_path, onnx_name)

os.system(
    f"pyinstaller "
    f"--add-data {onnx_path}{separator}ddddocr "
    f"-n ESurfingPy-CLI "
    f"-F "
    f"main.py"
)
