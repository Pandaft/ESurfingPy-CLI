import sys
import esurfingpy

if __name__ == '__main__':
    if len(sys.argv) == 1:
        gui = esurfingpy.Gui()
        gui.run()
    else:
        esurfingpy.cli()
