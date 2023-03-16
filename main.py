import sys

import esurfingpy

if __name__ == '__main__':
    if len(sys.argv) == 1:
        esurfingpy.log.warning("无参数运行，即将打开图形界面……")
        esurfingpy.Gui().run()
    else:
        esurfingpy.cli()
