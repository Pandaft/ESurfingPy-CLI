import platform
import ddddocr
import os

python = "python"
if platform.system() != "Windows":
    python += "3"

dir_path = os.path.dirname(ddddocr.__file__)
onnx_name = "common_old.onnx"
onnx_path = os.path.join(dir_path, onnx_name)

os.system(
    f"{python} -m nuitka "
    f"--assume-yes-for-downloads "
    f"--include-data-files={onnx_path}=ddddocr\\{onnx_name} "
    f"--output-dir=dist "
    f"--output-filename=ESurfingPy-CLI "
    f"--remove-output "
    f"--onefile "
    f"main.py"
)
