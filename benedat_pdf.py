#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""Modul pro generování sestav do pdf"""

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


import jagpdf
import benedat_cas as bcas


class Sestava():

    # rozměry papíru velikosti A4 (v jakých-si jednotkách se kterými pracuje jagpdf)
    a4w = 597.6
    a4h = 848.68
    # okraje
    okraje = 30
    # mezery
    mezera = 15
    sirka_sloupce = 85

    # konstruktor (vytvoření nové sestavy, nastavení implicitních hodnot)
    def __init__(self,soubor="sestava.pdf"):
        # připravení Pdf souboru
        self.sestava = jagpdf.create_file(soubor)

        # typ dokladu
        self.__typ_dokladu = 0
        # některé pomocné míry
        self._y = 0 
        self._x = 0
        self.radek = 15
        self.m_radek= 13
        self.adresa_y = 55
        self.adresa_l_x = 50
        
        ################ Jednotlivé informace v sestavě ##################
        # HLAVIČKA
        # informace v hlavičce vlevo
        self.__hlavicka_l = "Občanské sdružení BENEDIKTUS"
        # informace v hlavičce vpravo
        self.__hlavicka_r = "Příjmový pokladní doklad č."
        self.__kod = ""
        # ADRESA VLEVO
        # popis adresy vlevo
        self.__adresa_l_nadpis = ""
        # hlavní část adresy vlevo
        self.__adresa_l = ("Občanské sdružení BENEDIKTUS", "Klášterní 60", "583 01 Chotěboř")
        # doplňující informace vlevo
        self.__adresa_l_dalsi = ("IČ: 70868832", 
                            "DIČ: CZ70868832", 
                            "Mobil: +420 731 646 811", 
                            "E-mail: benediktus@centrum.cz",
                            "WWW: benediktus.infobar.cz")
        # ADRESA VPRAVO
        # popis adresy vpravo
        self.__adresa_r_nadpis = "Přijato od"
        # hlavní část adresy vpravo
        self.__adresa_r = ("Jan Novák", "Velká Lhota 111", "583 01 Chotěboř")
        # doplňující informace vpravo
        self.__adresa_r_dalsi = ()
        # DATUMY
        # datum vystavení
        self.__datum_vystaveni_nadpis = "Datum vystavení:"
        self.__datum_vystaveni = ""
        # datum platby
        self.__datum_platby_nadpis = "Datum platby:"
        self.__datum_platby = ""
        # Pokladna: Pokladna hlavní
        self.__pokladna_nadpis = "Pokladna: "
        self.__pokladna = "Pokladna hlavní";

        # firma není plátce dph
        self.__firma_neni_platcem_dph = "Firma není plátce DPH."
        # ZÁZNAMY
        # Souhrnný text co je fakturováno
        self.__souhrny_text = "Souhrn odlehčovací služby:"
        # jednotlivé záznamy jako seznam seznamů
        # [[datum, cas_od, cas_do, cas_celkem, dovoz, odvoz],[...],..]
        self.__zaznamy = [[]]
        # SOUHRN
        # souhrn z jednotlivých záznamů
        # [pocet_hodin, cena_os, pocet_cest, cena_cest]
        self.__souhrn = [0,0,0,0,0]

        # VYSTAVIL
        self.__vystavil = ""
        self.__vystavil_nadpis = "Vystavil: "

        # PODPIS ODBĚRATELE
        self.__podpis_odberatele_nadpis = "Podpis odběratele:"

        # PODPIS POKLADNÍKA
        self.__podpis_pokladnika_nadpis = "Podpis pokladníka:"

    ############## Funkce k nastavení jednotlivých informací v sestavě ###########
    # typ dokladu
    def typ_dokladu(self, tmp):
        self.__typ_dokladu = tmp

    # HLAVIČKA
    # informace v hlavičce vlevo
    def hlavicka_l(self, tmp):
        self.__hlavicka_l = tmp
    # informace v hlavičce vpravo
    def hlavicka_r(self, tmp):
        self.__hlavicka_r = tmp
    def kod(self, tmp):
        self.__kod= tmp
    # ADRESA VLEVO
    # popis adresy vlevo
    def adresa_l_nadpis(self, tmp):
        self.__adresa_l_nadpis = tmp
    # hlavní část adresy vlevo
    def adresa_l(self, tmp):
        self.__adresa_l = []
        for polozka in tmp:
            self.__adresa_l += polozka.split('|')
    # doplňující informace vlevo
    def adresa_l_dalsi(self, tmp):
        self.__adresa_l_dalsi = [] 
        for polozka in tmp:
            self.__adresa_l_dalsi += polozka.split('|')
    # ADRESA VPRAVO
    # popis adresy vpravo
    def adresa_r_nadpis(self, tmp):
        self.__adresa_r_nadpis = tmp
    # hlavní část adresy vpravo
    def adresa_r(self, tmp):
        self.__adresa_r = []
        for polozka in tmp:
            self.__adresa_r += polozka.split('|')
    # doplňující informace vpravo
    def adresa_r_dalsi(self, tmp):
        self.__adresa_r_dalsi = []
        for polozka in tmp:
            self.__adresa_r_dalsi += polozka.split('|')
    # DATUMY 
    # datum vystavení
    def datum_vystaveni(self, tmp):
        self.__datum_vystaveni = tmp
    # datum platby
    def datum_platby(self, tmp):
        self.__datum_platby = tmp
    # název pokladny
    def pokladna(self, tmp):
        self.__pokladna = tmp
    # ZÁZNAMY
    # souhrnný text
    def souhrnny_text(self, tmp):
        self.__souhrny_text = tmp
    # jednotlivé záznamy
    def zaznamy(self, tmp):
        self.__zaznamy = tmp
    #SOUHRN
    def souhrn(self, tmp):
        self.__souhrn = tmp
    # VYSTAVIL
    def vystavil(self, tmp):
        self.__vystavil = tmp

    



    # písma
    def regular(self,size=12):
        return self.sestava.font_load("file=fonts/LinLibertine_Re.ttf; size="+str(size)+"; enc=utf-8")
    def bold(self,size=12):
        return self.sestava.font_load("file=fonts/LinLibertine_Bd.ttf; size="+str(size)+"; enc=utf-8")
    def italic(self,size=12):
        return self.sestava.font_load("file=fonts/LinLibertine_It.ttf; size="+str(size)+"; enc=utf-8")
    def bold_italic(self,size=12):
        return self.sestava.font_load("file=fonts/LinLibertine_BI.ttf; size="+str(size)+"; enc=utf-8")

    def rozdily_typ_dokladu(self):
        if self.__typ_dokladu ==0:
            # hlavička (v pravo)
            self.__hlavicka_r = "Příjmový pokladní doklad č."
        
        elif self.__typ_dokladu ==1:
            # hlavička (v pravo)
            self.__hlavicka_r = "Výpis poskytnutých služeb"
            # datum platby
            self.__datum_platby_nadpis = ""
            self.__datum_platby = ""
            # Pokladna: Pokladna hlavní
            self.__pokladna_nadpis = ""
            self.__pokladna = "";
            # firma není plátce dph
            self.__firma_neni_platcem_dph = ""
            # PODPIS POKLADNÍKA
            self.__podpis_pokladnika_nadpis = "Podpis:"




    # vytvoření jedné sestavy
    def vytvor_sestavu(self):
        self.rozdily_typ_dokladu()
        self.sestava.page_start(Sestava.a4w,Sestava.a4h)
        self.c = self.sestava.page().canvas()
        
        # ============== VYKRESLENÍ JEDNÉ SESTAVY ====================
        # Hlavička vlevo
        self.c.text_font(self.bold(14))
        self.c.text(x(Sestava.okraje),y(Sestava.okraje), self.__hlavicka_l)
        # Hlavička vpravo
        self.c.text(x(-self.bold(14).advance(self.__hlavicka_r+self.__kod)-Sestava.okraje),
                    y(Sestava.okraje), self.__hlavicka_r+self.__kod)

        # Adresa vlevo
        self.c.text_font(self.regular(9))
        self._x = self.adresa_l_x
        self._y = self.adresa_y
        self.c.text(x(self._x),y(self._y), self.__adresa_l_nadpis)
        self.c.text_font(self.bold())
        tmp_vyska_adresy = 2 * self.radek 
        for tmp_radek in self.__adresa_l:
            self._y += self.radek
            tmp_vyska_adresy += self.radek
            self.c.text(x(self._x),y(self._y), tmp_radek)
        self._y += 10
        tmp_vyska_adresy += 10
        self.c.text_font(self.regular())
        for tmp_radek in self.__adresa_l_dalsi:
            self._y += self.radek
            tmp_vyska_adresy += self.radek
            self.c.text(x(self._x),y(self._y), tmp_radek)

        
        # Adresa vpravo
        self.c.text_font(self.regular(9))
        self._y = self.adresa_y
        self._x = Sestava.a4w/2 + self.okraje
        self.c.text(x(self._x),y(self._y), self.__adresa_r_nadpis)
        self.c.text_font(self.bold())
        tmp_vyska_adresy2 = 2 * self.radek
        for tmp_radek in self.__adresa_r:
            if not tmp_radek:
                continue
            self._y += self.radek
            tmp_vyska_adresy2 += self.radek
            self.c.text(x(self._x),y(self._y), tmp_radek)
        self._y += 10
        tmp_vyska_adresy2 += 10
        self.c.text_font(self.regular())
        for tmp_radek in self.__adresa_r_dalsi:
            if not tmp_radek:
                continue
            self._y += self.radek
            tmp_vyska_adresy2 += self.radek
            self.c.text(x(self._x),y(self._y), tmp_radek)
        
        if tmp_vyska_adresy < tmp_vyska_adresy2:
            tmp_vyska_adresy = tmp_vyska_adresy2
        
        # vykreslení rámečku kolem adres
        self.c.line_width(0.5)
        self.c.rectangle(x(Sestava.okraje),
                        y(self.adresa_y-self.radek),Sestava.a4w/2-Sestava.okraje,-tmp_vyska_adresy)
        self.c.path_paint('s')
        self.c.line_width(2)
#        self.c.rectangle(x(Sestava.a4w/2),y(40),Sestava.a4w/2-Sestava.okraje,-tmp_vyska_adresy)
#        self.c.rectangle(x(Sestava.a4w/2),y(40),Sestava.a4w/2-Sestava.okraje,-(tmp_vyska_adresy-60))
        self.c.rectangle(x(Sestava.a4w/2),y(40),Sestava.a4w/2-Sestava.okraje,-tmp_vyska_adresy2)
        self.c.path_paint('s')

        # výpis datumu(ů)
#        self.c.text(x(self._x),y(self._y), str(tmp_vyska_adresy))
#        self.c.text(x(self._x),y(self._y + self.radek), str(tmp_vyska_adresy2))
        tmp_vrsek_datumu = self._y
        #datum vystavení
        self._y = self.adresa_y + tmp_vyska_adresy + Sestava.mezera - (6 * self.radek)
        self.c.text_font(self.regular(12))
        self.c.text(x(self._x), y(self._y), str(self.__datum_vystaveni_nadpis))
        self.c.text_font(self.bold(12))
        self.c.text(x(self._x + 100), y(self._y), str(self.__datum_vystaveni))
        #datum platby
        self._y += self.radek
        self.c.text_font(self.regular(12))
        self.c.text(x(self._x), y(self._y), str(self.__datum_platby_nadpis))
        self.c.text_font(self.bold(12))
        self.c.text(x(self._x + 100), y(self._y), str(self.__datum_platby))
        # Pokladna: Pokladna hlavní
        self._y += self.radek
        self.c.text_font(self.regular(12))
        self.c.text(x(self._x), y(self._y), str(self.__pokladna_nadpis))
        self.c.text_font(self.bold(12))
        self.c.text(x(self._x + 100), y(self._y), str(self.__pokladna))       
        # firma není plátcem DPH
        self._y += self.radek
        self.c.text_font(self.bold(10))
        self.c.text(x(self._x), y(self._y), str(self.__firma_neni_platcem_dph))
        # vykreslení rámečků kolem datumu
        self._y = tmp_vrsek_datumu
        self.c.line_width(0.5)
        self.c.rectangle(x(Sestava.a4w/2),
                y(self._y+self.radek),
                Sestava.a4w/2-Sestava.okraje,
                -(tmp_vyska_adresy-tmp_vyska_adresy2))
        self.c.path_paint('s')

        # výpis záznamů
        # výpis souhrnného textu
        self._x = Sestava.okraje + 1*Sestava.mezera
        self._y = self.adresa_y + tmp_vyska_adresy #+ Sestava.mezera
        self.c.text_font(self.bold(12))
        self.c.text(x(self._x), y(self._y), self.__souhrny_text)

        # výpis popisků
        self.c.text_font(self.bold(10))
        self._x = Sestava.okraje + 2*Sestava.mezera
        self._y = self._y + self.radek
        sloupec = 0
        for popisek in ('datum', 'čas od', 'čas do', 'celkem', 'dovoz', 'odvoz'):
            self.c.text(x(self._x + sloupec * Sestava.sirka_sloupce), y(self._y), popisek)
            sloupec += 1

        # čáry okolo popisků
        self.c.line_width(0.5)
        self._x = Sestava.okraje + Sestava.mezera
#        self._y = self.adresa_y + tmp_vyska_adresy + Sestava.mezera
        for i in range(5):
            self.c.move_to(x(self._x + (i+1) * Sestava.sirka_sloupce), y(self._y+5))
            self.c.line_to(x(self._x + (i+1) * Sestava.sirka_sloupce), y(self._y-10))
            self.c.path_paint('s')
        self.c.move_to(x(self._x), y(self._y+5))
        self.c.line_to(x(self._x + 6 * Sestava.sirka_sloupce), y(self._y+5))
        self.c.path_paint('s')

        # výpis záznamů
        self.c.text_font(self.regular(11))
        self._x = Sestava.okraje + 2 * Sestava.mezera
        self._y = self._y + 1.2 * self.radek
        if self.__zaznamy:
            for datum, od, do, celkem, dovoz, odvoz in self.__zaznamy:
                self.c.text(x(self._x + 0 * Sestava.sirka_sloupce + 
                    (40 - self.regular(12).advance(bcas.preved_datum(datum,0)))),
                    y(self._y), bcas.preved_datum(datum,0))
                self.c.text(x(self._x + 1 * Sestava.sirka_sloupce +
                    (23 - self.regular(12).advance(str(od)))), 
                    y(self._y), str(od))
                self.c.text(x(self._x + 2 * Sestava.sirka_sloupce +
                    (23 - self.regular(12).advance(str(do)))), 
                    y(self._y), str(do))
                self.c.text(x(self._x + 3 * Sestava.sirka_sloupce), y(self._y), str(round(celkem, 2)))
                if dovoz:
                    self.c.text(x(self._x + 4 * Sestava.sirka_sloupce), y(self._y), 'x')
                if odvoz:
                    self.c.text(x(self._x + 5 * Sestava.sirka_sloupce), y(self._y), 'x')
                self._y = self._y + self.m_radek

        # dolní oddělovací čára
        self._x = Sestava.okraje + Sestava.mezera
        self.c.move_to(x(self._x), y(self._y-self.radek+5))
        self.c.line_to(x(self._x + 6 * Sestava.sirka_sloupce), y(self._y-self.radek+5))
        self.c.path_paint('s')

        # výpis souhrnu
        # popisky
        self.c.text_font(self.bold(10))
        self._x = Sestava.okraje + 2*Sestava.mezera + 2*self.sirka_sloupce
        self._y = self._y + Sestava.mezera
        self.c.text(x(self._x + 0 * Sestava.sirka_sloupce), y(self._y), "položka")
        self.c.text(x(self._x + 2 * Sestava.sirka_sloupce), y(self._y), "celkem")
        self.c.text(x(self._x + 3 * Sestava.sirka_sloupce), y(self._y), "cena celkem")
        # hodnoty
        self.c.text_font(self.regular(12))
        self._y += self.m_radek
        self.c.text(x(self._x + 0 * Sestava.sirka_sloupce), y(self._y), "odlehčovací služba")
        self.c.text(x(self._x + 2 * Sestava.sirka_sloupce), y(self._y), str(round(self.__souhrn[0],2))+" hodin")
        self.c.text(x(self._x + 3 * Sestava.sirka_sloupce + 
                    (50 - self.regular(12).advance(str('%0.2f' % self.__souhrn[1])+" kč"))),
                    y(self._y), str('%0.2f' % self.__souhrn[1])+" kč")
        self._y += self.m_radek
        self.c.text(x(self._x + 0 * Sestava.sirka_sloupce), y(self._y), "cesty")
        self.c.text(x(self._x + 2 * Sestava.sirka_sloupce), y(self._y), str(self.__souhrn[2]))
        self.c.text(x(self._x + 3 * Sestava.sirka_sloupce + 
                    (50 - self.regular(12).advance(str('%0.2f' % self.__souhrn[3])+" kč"))), 
                    y(self._y), str('%0.2f' % self.__souhrn[3])+" kč")
        self.c.text_font(self.bold(12))
        self._y += self.m_radek
        self.c.text(x(self._x + 0 * Sestava.sirka_sloupce), y(self._y), "celkem")
        self.c.text(x(self._x + 3 * Sestava.sirka_sloupce + 
                    (50 - self.bold(12).advance(str('%0.2f' % self.__souhrn[4])+" kč"))), 
                    y(self._y), str('%0.2f' % self.__souhrn[4])+" kč")

        self._x = Sestava.okraje + 1 * Sestava.mezera
        self._y = self._y + 2 * Sestava.mezera
        # čára nad Vystavil:
        self.c.move_to(x(self._x), y(self._y-self.radek))
        self.c.line_to(x(-self._x), y(self._y-self.radek))
#        self.c.line_to(x(self._x + 2 * Sestava.sirka_sloupce), y(self._y-self.radek))
        self.c.path_paint('s')
        # Vystavil
        self._y += Sestava.mezera
        self._x = Sestava.okraje + 2 * Sestava.mezera
        self.c.text_font(self.regular(12))
        self.c.text(x(self._x), y(self._y), self.__vystavil_nadpis)
        self.c.text_font(self.bold(12))
        self.c.text(x(self._x + 50), y(self._y), self.__vystavil)
        # podpis odběratele
        self._x = Sestava.a4w/2 + self.okraje + Sestava.mezera
        self.c.text_font(self.regular(12))
        self.c.text(x(self._x), y(self._y), self.__podpis_odberatele_nadpis)
        # podpis pokladníka
        self._y += Sestava.mezera*1.5
        self._x = Sestava.okraje + 2 * Sestava.mezera
        self.c.text_font(self.regular(12))
        self.c.text(x(self._x), y(self._y), self.__podpis_pokladnika_nadpis)


       




        



        self.sestava.page_end()

    # destruktor, ukončení celé sestavy
#    def __del__(self):
#        self.sestava.finalize()
#        pass

    def finalize(self):
        self.sestava.finalize()


# POMOCNÉ FUNKCE
# Výpočet souřadnic od levého horního rohu (s mínusem obráceně)
def x(x):
    if x < 0:
        return Sestava.a4w + x
    else:
        return x
def y(y):
    if y < 0:
        return -y
    else:
        return Sestava.a4h - y




def test():
    s = Sestava()
    s.hlavicka_l("VZOR!")
    s.vytvor_sestavu()
    s.vytvor_sestavu()
    s.finalize()


if __name__ == "__main__":
    test()







