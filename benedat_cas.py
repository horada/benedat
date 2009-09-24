#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""pomocný modul pro práci s datem a časem"""

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


import re
import time
import string



def zjisti_format_data(datum_text):
    """funkce pro zjištění formátu zadaného data
    d.m.[rr]rr    dd.mm.[rr]rr      tecky_cely
    d.m[.]  dd.mm[.]                tecky_den_mesic
    d[.] dd[.]                      tecky_den
    rrrr-mm-dd                      pomlcky_cely"""

    reg_vyraz_tecky_cely = re.compile(r'''^\d?\d\.\d?\d\.(\d\d)?\d\d$''')
    reg_vyraz_tecky_den_mesic = re.compile(r'''^\d?\d\.\d?\d\.?$''')
    reg_vyraz_tecky_den = re.compile(r'''^\d?\d\.?$''')
    reg_vyraz_pomlcky_cely = re.compile(r'''^\d\d\d\d-\d\d-\d\d$''')

    if reg_vyraz_tecky_cely.match(datum_text):
#        print "cely"
        return 1
    elif reg_vyraz_tecky_den_mesic.match(datum_text):
#        print "den_mesic"
        return 2
    elif reg_vyraz_tecky_den.match(datum_text):
#        print "den"
        return 3
    elif reg_vyraz_pomlcky_cely.match(datum_text):
        return 4
    else:
        return None


def preved_datum_na_seznam_ddmmrrrr(datum_text, mesic=None, rok=None):
    """funkce převede datum zadaný v textu na datum dd.mm.rrrr
    případně doplní mesic a rok podle proměnných (při nezadání aktuální)"""
    if not mesic:
        mesic = time.strftime('%m')
    if not rok:
        rok = time.strftime('%Y')
    format_data = zjisti_format_data(datum_text)

    if format_data == 1:
        datum = string.split(datum_text, '.')
        datum[0] = datum[0].rjust(2, '0')
        datum[1] = datum[1].rjust(2,'0')
        if len(datum[2])<4:
            datum[2] = rok[:2] + datum[2]
    elif format_data == 2:
        datum = string.split(datum_text, '.')
        datum = datum[:2]
        datum[0] = datum[0].rjust(2,'0')
        datum[1] = datum[1].rjust(2,'0')
        datum.append(rok)
    elif format_data == 3:
        datum = string.split(datum_text, '.')
        datum = datum[:1]
        datum[0] = datum[0].rjust(2,'0')
        datum.append(mesic)
        datum.append(rok)
    elif format_data == 4:
        datum = string.split(datum_text, '-')
        datum.reverse()
    else:
        return None

    return datum


def preved_datum(datum_text, format=0,predchozi = None):
    """převedení datumu na nějaký formát
    0   dd.mm.rrrr
    1   dd-mm-rrrr
    2   rrrr-mm-dd
    """
    if datum_text.strip() == "+":
        datum_text = datum_plus(predchozi['den'] + '.' + predchozi['mesic'] + '.' + predchozi['rok'])
#        datum = [str(int(predchozi['den'])+1).rjust(2,'0'), predchozi['mesic'], predchozi['rok']]
    if datum_text.strip() == "-":
        datum_text = datum_plus(predchozi['den'] + '.' + predchozi['mesic'] + '.' + predchozi['rok'], -1)
#        datum = [str(int(predchozi['den'])-1).rjust(2,'0'), predchozi['mesic'], predchozi['rok']]
#    print datum_text + "\t",
    datum = preved_datum_na_seznam_ddmmrrrr(datum_text)
    if datum:
        if format == 0:
            return str(int(datum[0])) + "." + str(int(datum[1])) + "." + str(int(datum[2]))
        elif format == 1:
            return datum[0] + "-" + datum[1] + "-" + datum[2]
        elif format == 2:
            return datum[2] + "-" + datum[1] + "-" + datum[0]
        else:
            return None
    else:
        return None

def den(datum_text):
    """vrátí číslo den ze zadaného datumu"""
    datum = preved_datum_na_seznam_ddmmrrrr(datum_text)
    return datum[0]
            
def mesic(datum_text):
    """vrátí číslo měsíce ze zadaného datumu"""
    datum = preved_datum_na_seznam_ddmmrrrr(datum_text)
    return datum[1]
            
def rok(datum_text):
    """vrátí číslo roku ze zadaného datumu"""
    datum = preved_datum_na_seznam_ddmmrrrr(datum_text)
    return datum[2]
            
def datum_plus(datum_text,pocet_dni=1):
    """Přičtení počtu dní k zadanému datu. Defaultně 1 den."""
    datum = preved_datum_na_seznam_ddmmrrrr(datum_text)
    datum_format = zjisti_format_data(datum_text)
    if not datum:
        return None
    datum_text = time.strftime('%d.%m.%Y',
            time.localtime(
                time.mktime(
                    time.strptime(datum[0]+'.'+datum[1]+'.'+datum[2],
                        '%d.%m.%Y'))+pocet_dni*86400))
    return datum_text
#    if datum_format == 1:
#        return datum_text
#    else:
#        return preved_datum(datum_text, datum_format)

    
def zjisti_format_casu(cas_text):
    """funkce pro zjištění formátu zadaného času
    hh:mm               dvojtecka_cely
    hh[:]               dvojtecka_hodina
    hh-mm               pomlcka_cely
    hh-                 pomlcka_hodina
    hh,mm               carka_cely
    hhmm                dohromady_cely"""

    reg_vyraz_dvojtecka_cely = re.compile(r'''^\d?\d:\d?\d$''')
    reg_vyraz_dvojtecka_hodina = re.compile(r'''^\d?\d:?$''')
    reg_vyraz_pomlcka_cely = re.compile(r'''^\d?\d-\d?\d$''')
    reg_vyraz_pomlcka_hodina = re.compile(r'''^\d?\d-$''')
    reg_vyraz_carka_cely = re.compile(r'''^\d?\d,\d?\d$''')
    reg_vyraz_tecka_cely = re.compile(r'''^\d?\d\.\d?\d$''')
    reg_vyraz_dohromady_cely= re.compile(r'''^\d?\d\d\d$''')
    reg_vyraz_jen_hodina = re.compile(r'''^\d?\d$''')

    if reg_vyraz_dvojtecka_cely.match(cas_text):
        return 1
    if reg_vyraz_dvojtecka_hodina.match(cas_text):
        return 2
    if reg_vyraz_pomlcka_cely.match(cas_text):
        return 3
    if reg_vyraz_pomlcka_hodina.match(cas_text):
        return 4
    if reg_vyraz_carka_cely.match(cas_text):
        return 5
    if reg_vyraz_tecka_cely.match(cas_text):
        return 6
    if reg_vyraz_dohromady_cely.match(cas_text):
        return 7
    if reg_vyraz_jen_hodina.match(cas_text):
        return 8


def preved_cas_na_seznam_hhmm(cas_text):
    """funkce převede zadaný čas v textu na čas rozdělený do seznamu ['hh', 'mm']"""
    format_casu = zjisti_format_casu(cas_text)

    if format_casu == 1:
        cas = string.split(cas_text, ':')
        cas[0] = cas[0].rjust(2, '0')
        cas[1] = cas[1].rjust(2, '0')
    elif format_casu == 2:
        cas = string.split(cas_text, ':')
        cas = cas[:1]
        cas[0] = cas[0].rjust(2, '0')
        cas.append('00')
    elif format_casu == 3:
        cas = string.split(cas_text, '-')
        cas[0] = cas[0].rjust(2, '0')
        cas[1] = cas[1].rjust(2, '0')
    elif format_casu == 4:
        cas = string.split(cas_text, '-')
        cas = cas[:1]
        cas[0] = cas[0].rjust(2, '0')
        cas.append('00')
    elif format_casu == 5:
        cas = string.split(cas_text, ',')
        cas[0] = cas[0].rjust(2, '0')
        cas[1] = cas[1].rjust(2, '0')
    elif format_casu == 6:
        cas = string.split(cas_text, '.')
        cas[0] = cas[0].rjust(2, '0')
        cas[1] = cas[1].rjust(2, '0')
    elif format_casu == 7:
        cas_text = cas_text.rjust(4, '0')
        cas = [cas_text[0:2], cas_text[2:4]]
    elif format_casu == 8:
        cas_text = cas_text.rjust(2, '0')
        cast = [cas_text, 00]
    else:
        return None
    return cas


def preved_cas(cas_text, format=0):
    """převedení času na nějaký formát
    0   hh:mm
    1   hh-mm
    """
    
    cas = preved_cas_na_seznam_hhmm(cas_text)
    if cas:
        if format == 0:
            return str(int(cas[0])) + ":" + cas[1]
        elif format == 0:
            return cas[0] + "-" + cas[1]
        else:
            return None
    else:
        return None


def test():
#    print zjisti_format_data("8.7.2009")
#    print zjisti_format_data("8.7.20098")
#    print zjisti_format_data("8.7.2009x")
#    print zjisti_format_data("08.7.2009")
#    print zjisti_format_data("8.07.2009")
#    print zjisti_format_data("08.07.2009")
#    print zjisti_format_data("8.7.09")
#    print zjisti_format_data("8.7.")
#    print zjisti_format_data("8.7")
#    print zjisti_format_data("8.")
#    print zjisti_format_data("8")
#    print zjisti_format_data("8.8.8")
#    print zjisti_format_data("88888")
#    print zjisti_format_data("8.7,")
#    print zjisti_format_data("XX")
   
#    print preved_datum_na_seznam_ddmmrrrr("8.7.2009")
#    print preved_datum_na_seznam_ddmmrrrr("8.7.20098")
#    print preved_datum_na_seznam_ddmmrrrr("8.7.2009x")
#    print preved_datum_na_seznam_ddmmrrrr("08.7.2009")
#    print preved_datum_na_seznam_ddmmrrrr("8.07.2009")
#    print preved_datum_na_seznam_ddmmrrrr("08.07.2009")
#    print preved_datum_na_seznam_ddmmrrrr("8.7.09")
#    print preved_datum_na_seznam_ddmmrrrr("8.7.")
#    print preved_datum_na_seznam_ddmmrrrr("8.7")
#    print preved_datum_na_seznam_ddmmrrrr("8.")
#    print preved_datum_na_seznam_ddmmrrrr("8")
#    print preved_datum_na_seznam_ddmmrrrr("8.8.8")
#    print preved_datum_na_seznam_ddmmrrrr("88888")
#    print preved_datum_na_seznam_ddmmrrrr("8.7,")
#    print preved_datum_na_seznam_ddmmrrrr("XX")

 
#    format = 0
#    print preved_datum("8.7.2009", format)
#    print preved_datum("8.7.20098", format)
#    print preved_datum("8.7.2009x", format)
#    print preved_datum("08.7.2009", format)
#    print preved_datum("18.07.2009", format)
#    print preved_datum("08.07.2009", format)
#    print preved_datum("8.7.09", format)
#    print preved_datum("8.7.", format)
#    print preved_datum("8.7", format)
#    print preved_datum("18.", format)
#    print preved_datum("28", format)
#    print preved_datum("8.8.8", format)
#    print preved_datum("88888", format)
#    print preved_datum("8.7,", format)

    datumy = ['27.8.2009',
            '27-08-2009',
            '2009-08-27']
    for datum in datumy:
        print datum,
        print '\t',
        print datum_plus(datum,20)

#    print preved_datum("XX", format)

#    casy = ['20:1',
#            '11:10',
#            '10:-',
#            '15-',
#            '05',
#            '08',
#            '8',
#            '6:',
#            '08:',
#            '08-05',
#            '08-5',
#            '08-',
#            '08,2',
#            '09,02',
#            '08,2',
#            '09:00']
#    for cas in casy:
#        print cas,
#        print "\t",
#        print preved_cas(cas)




if __name__ == "__main__":
    test()

