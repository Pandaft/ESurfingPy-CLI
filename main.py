import sys

import esurfingpy

if __name__ == '__main__':
    if len(sys.argv) == 1:
        esurfingpy.Gui().run()
    else:
        esurfingpy.cli()
