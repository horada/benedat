#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""Modul pro export dat do csv"""

#
# $Date: 2009-10-08 21:34:21 +0200 (Čt, 08 říj 2009) $
# $Revision: 67 $
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

import csv



class Souhrn_csv:
    def __init__(self, soubor="souhrn.csv"):
        self.soubor=soubor
        self.o = open(soubor, "w")
        self.csv = csv.writer(self.o,dialect='excel',delimiter=';')


    def zapis_radek(self, data):
        self.csv.writerow(data)


    def close(self):
        self.o.close()
