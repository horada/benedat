#!/usr/bin/env python
#-*- coding: utf-8 -*-

#
# $Date$
# $Revision$
#

#
# BeneDat - program pro výpočet ceny za poskytnuté služby klientům občanského sdružení
# 
# Copyright (C)2009 Daniel Horák
# 
# Tento program je svobodný software; můžete jej šířit a modifikovat podle
# ustanovení GNU General Public License, vydávané Free Software
# Foundation; a to buď verze 3 této licence anebo (podle vašeho uvážení)
# kterékoli pozdější verze.
# 
# Tento program je rozšiřován v naději, že bude užitečný, avšak BEZ
# JAKÉKOLI ZÁRUKY; neposkytují se ani odvozené záruky PRODEJNOSTI anebo
# VHODNOSTI PRO URČITÝ ÚČEL. Další podrobnosti hledejte ve GNU General Public License.
# 
# Kopii GNU General Public License jste měl obdržet spolu s tímto
# programem; pokud se tak nestalo, napište o ni Free Software Foundation,
# Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
# 



import sys
try:
    import pygtk
    pygtk.require("2.16")
except:
    pass
try:
    import gtk
    import gtk.glade
except:
    print "ERROR: Import module gtk or gtk.glade failed."
    sys.exit(1)

import os

import benedat_config as bconf
import benedat_gui as gui



def main():
    # jako pracovní adresář nastavíme adresář se skriptem
    if os.path.dirname(sys.argv[0]):
        os.chdir(os.path.dirname(sys.argv[0]))

    # načtení/vytvoření konfigurace 
    konf = bconf.Konfigurace("benedat.conf")
    konf.nacteni_konfigurace_ze_souboru()
    if not konf.volba("otevreny_soubor"):
        konf["otevreny_soubor"] = None

    # nastavení dalších konfiguračních voleb
    default_konf_volby = {  'pokladna': "HP",
                            #'kontrola_duplicity': "true",
                            'kod_predkontace': "6023-odleh",
                            'kod_cleneni_dph': "nonSubsume",
                            'kod_strediska': "0011-vl.zd",
                            'kod_cinnosti': "odl",
                            'ico': "0000",
                            'aplikace': "BeneDat",
                            'poznamka_k_exportu': "Převod dat z programu BeneDat"}
    for volba in default_konf_volby.keys():
        if not konf.volba(volba):
            konf[volba] = default_konf_volby[volba]

  

    benedat = gui.BenedatHlavniOkno("benedat_gui.glade", konf)
    gtk.main()

    

    konf.ulozeni_konfigurace_do_souboru()

if __name__ == "__main__":
    main()
    
