import sys

from esurfingpy import log
from esurfingpy.cli import cli, Gui

if __name__ == '__main__':
    if len(sys.argv) == 1:
        log.warning("无参数运行，即将打开图形界面……")
        Gui().run()
    else:
        cli()
