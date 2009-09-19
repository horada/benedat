#!/usr/bin/env python
#-*- coding: utf-8 -*-


try:
    import pygtk
    pygtk.require("2.16")
except:
    pass
try:
    import gtk
    import gtk.glade
except:
    sys.exit(1)

import sys
import os

import benedat_config as bconf
import benedat_gui as gui



def main():
    # jako pracovní adresář nastavíme adresář se skriptem
    os.chdir(os.path.dirname(sys.argv[0]))

    # načtení/vytvoření konfigurace 
    konf = bconf.Konfigurace("benedat.conf")
    konf.nacteni_konfigurace_ze_souboru()
    if not konf.volba("otevreny_soubor"):
        konf["otevreny_soubor"] = None
   

    benedat = gui.BenedatHlavniOkno("benedat_gui.glade", konf)
    gtk.main()

    

    konf.ulozeni_konfigurace_do_souboru()

if __name__ == "__main__":
    main()
    
