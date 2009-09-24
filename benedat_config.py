#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""Modul pro ukládání, načítání a přístup ke konfiguraci"""

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


import string
import re
import os

class Konfigurace(dict):
    """Třída pro ukládání, načítání a přístup ke konfiguraci"""
    def __init__(self, konfiguracni_soubor = None):
        """inicializace modulu"""
        self.nastav_konfiguracni_soubor(konfiguracni_soubor)


    def __str__(self):
        """pro výpis konfigurace"""
        tmp = ""
        for volba in self.keys():
            if type(self[volba]) == str:
                tmp += str(volba)
                tmp += '='
                tmp += '"'
                tmp += str(self[volba])
                tmp += '"'
                tmp += '\n'
            else:
                tmp += str(volba)
                tmp += '='
                tmp += str(self[volba])
                tmp += '\n'
        return tmp

    

    def nastav_konfiguracni_soubor(self, konfiguracni_soubor):
        self.konfiguracni_soubor = konfiguracni_soubor

    def nacteni_konfigurace_ze_souboru(self):
        """Načtení konfigurace ze souboru"""
        # Je zadán nějaký soubor a existuje?
        if not self.konfiguracni_soubor:
            return -1
        if not os.path.isfile(self.konfiguracni_soubor):
            return -1

        # načtení souboru
        souborovyobjekt=open(self.konfiguracni_soubor,'r')
        radky = souborovyobjekt.readlines()
        souborovyobjekt.close()

        reg_vyraz_komentare = re.compile(r"\#.*")
        reg_vyraz_uvozovek = re.compile(r'''(^['"])|(["']$)''')
        for radek in radky:
            # odstranění komentářů
            radek =reg_vyraz_komentare.sub("", radek)
            # odstranění přebytečných mezer
            radek = string.strip(radek)
            # odstranění prázdných řádků
            if radek == "":
                continue
            # rozdělení na volbu a hodnotu
            radek = string.split(radek, "=", 1)
            # odstranění přebytečných mezer
            radek[0]=string.strip(radek[0])
            radek[1]=string.strip(radek[1])
            # odstranění uvozovek či apostrofů na začátku 
            #a konci řetězců (pokud existují)
            radek[1] = reg_vyraz_uvozovek.sub("", radek[1])
            # uložení hodnoty k volbě
            self[radek[0]] = radek[1]

        return self
    
    def ulozeni_konfigurace_do_souboru(self):
        """Uložení konfigurace do souboru"""
        # Je zadán nějaký soubor?
        if not self.konfiguracni_soubor:
            return -1

        souborovyobjekt=open(self.konfiguracni_soubor,'w')
        
        souborovyobjekt.write(str(self))

        souborovyobjekt.close()

    def nastav_volby(self, volby):
        """Nastavení více konfiguračních voleb (ze slovníku)"""
        for volba in volby.keys():
            self[volba]=volby[volba]

    def nastav_volbu(self, volba, hodnota):
        """Nastavení jedné konfigurační volby"""
        self[volba]=hodnota

    def volba(self,volba, hodnota=None):
        """Vrátí hodnotu volby - pokud neexistuje vrátí None"""
        if hodnota:
            self[volba] = hodnota
        else:
            if self.has_key(volba):
                return self[volba]
            else:
                return None

        







def test():
    konf = Konfigurace("pokus.conf")

    dict_konf = {
            'soubor': "Pokus.txt",
            'soubor2': "jiny_pokus",
            'pocet': 3,
            'pozdrav': "Dobrý den"
            }
    konf.nastav_volby(dict_konf)
#
#
    konf.ulozeni_konfigurace_do_souboru()
#    print konf
#    print "======================"
#
#    konf2 = Konfigurace()
#    konf2.nastav_konfiguracni_soubor("pokus.conf")
#    konf2.nacteni_konfigurace_ze_souboru()
#    print konf2
#    print "======================"
#
    print konf.volba("pozdrav")
    print konf.volba("pozdrav2")

#    print konf.nacteni_konfigurace_ze_souboru()

if __name__ == '__main__':
    test()
