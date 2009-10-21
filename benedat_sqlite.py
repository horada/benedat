#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""Modul zprostředkující komunikaci s sqlite databází."""

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


from sqlite3 import dbapi2 as sqlite
import sys
import os
import benedat_chyby as err
from benedat_log import *
import time

AKTUALNI_VERZE_DB = "5"

class Db:
    def __init__(self, soubor, novy=False):
        """Inicializace provede otevření existující databáze (a její základní ověření)
        nebo vytvoření nové a založení základní struktury."""
        if novy and os.path.isfile(soubor):
            os.remove(soubor)
                        
        # detekce existence souboru
        if os.path.isfile(soubor):
            # Soubor existuje - otevření a ověření db
#            log("Otevírám soubor %s." % soub
            self.otevreni_db(soubor)
        else:
            # Soubor neexistuje - vytvoření nového
            self.vytvoreni_db(soubor)
            
    def __del__(self):
        """Uzavření databáze při ukončení"""
        try:
            if type(self.databaze) == sqlite.Connection:
                self.databaze.close()
        except AttributeError, e:
            pass

    def vytvoreni_db(self, soubor):
        """Vytvoření nového databázového souboru a základní doplnění"""
#        log("Vytvářím nový soubor %s." % soubor)
        try:
            self.databaze = sqlite.connect(soubor)
        except sqlite.OperationalError, e:
            #print "CHYBA"
            #print e
            raise err.ChybaSoubor("Nemohu vytvořit soubor %s! (%s)" % (soubor,e))
        # Vytvoření základní struktury tabulek
        try:
            self.databaze.text_factory = lambda x: unicode(x, "utf-8", "ignore")
            # Vytvoření tabulky klienti
            self.databaze.execute("""
                CREATE TABLE klienti (
                    id_klienta INTEGER NOT NULL ,
                    jmeno TEXT(50) NOT NULL ,
                    prijmeni TEXT(50) NOT NULL ,
                    adresa TEXT(200) ,
                    telefon TEXT(50) ,
                    mobil1 TEXT(50) ,
                    mobil2 TEXT(50) ,
                    pozn TEXT(500) ,
                    os NUMERIC NOT NULL ,
                    oa NUMERIC NOT NULL ,
                    km_os INTEGER ,
                    os_pausal INTEGER ,
                    os_cena_do INTEGER ,
                    os_cena_mezi INTEGER ,
                    os_cena_nad INTEGER ,
                    os_pausalHodin INTEGER ,
                    PRIMARY KEY (id_klienta)
                );"""
            )
            # Vytvoření tabulky zaznamy_os
            self.databaze.execute("""
                CREATE TABLE zaznamy_os (
                    id INTEGER NOT NULL ,
                    id_klienta INTEGER NOT NULL ,
                    datum TEXT(15) NOT NULL ,
                    cas_od TEXT(15) NOT NULL ,
                    cas_do TEXT(15) NOT NULL ,
                    dovoz NUMERIC NOT NULL ,
                    odvoz NUMERIC NOT NULL ,
                    PRIMARY KEY (id)
                    );                    
            """
            )
            # Vytvoření tabulky nastavení
            self.databaze.execute("""
                CREATE TABLE nastaveni (
                    volba TEXT(50) NOT NULL ,
                    hodnota TEXT(100) ,
                    pozn TEXT(300) , 
                    PRIMARY KEY (volba)
                    );                    
            """
            )
            # Vložení hodnoty verze db do tabulky nastaveni
            self.databaze.execute("""
                INSERT INTO nastaveni (volba, hodnota, pozn)
                    values ('verze', ?, 
                        'Verze databáze (podle této hodnoty se též zjišťuje korektnost databáze')""", (AKTUALNI_VERZE_DB))
            # Vložení základního nastavení
            nastaveni = (('cestovne_os_cena_za_litr','33',u'Cestovné - cena za litr'),
                        ('cestovne_os_exp','0.85',u'Cestovné - exp'),
                        ('cestovne_os_k','15',u'Cestovné - konstanta k'),
                        ('cestovne_os_nastupni_sazba','6',u'Cestovné - Nástupní sazba'),
                        ('cestovne_os_podil_klienta','0.5',u'Cestovné - podíl klienta'),
                        ('kod_stala_cast','XXXX',u'Kód faktury (stálá část)'),
                        ('kod_promenna_cast','0000',u'Kód faktury (proměnná část)'),
                        ('dolni_hranice_poctu_hodin','30','Dolní hranice pro počet hodin OS'),
                        ('horni_hranice_poctu_hodin','60','Horní hranice pro počet hodin OS'),
                        ('adresa','Občanské sdružení BENEDIKTUS|Klášterní 60|583 01 Chotěboř','Adresa uváděná v sestavách'),
                        ('adresa_dalsi','IČ: 70868832|DIČ: CZ70868832|Mobil: +420 731 646 811|E-mail: benediktus@centrum.cz|WWW: benediktus.infobar.cz','Doplňující informace v adrese'),
                        #('','',''),
                        ('vystavil','',u'Kdo vystavil příjmový doklad'))
            for t in nastaveni:
                self.databaze.execute("""INSERT INTO nastaveni (volba, hodnota, pozn)
                    values (?, ?, ?)""", t)
            self.databaze.commit()
            self.databaze.create_function('spoj', 2, spoj_s_mezerou)
        except sqlite.Error, e:
            log(e)

    def otevreni_db(self, soubor):
        """Otevření a ověření databázového souboru"""
        try:
            self.databaze = sqlite.connect(soubor)
            self.databaze.text_factory = lambda x: unicode(x, "utf-8", "ignore")
            self.databaze.create_function('spoj', 2, spoj_s_mezerou)
        except sqlite.OperationalError, e:
            raise err.ChybaSoubor("Nemohu otevřít soubor %s! (%s)" % (soubor,e))
        # Ověření korektnosti a verze db
        try:
            vystup = self.databaze.execute("""
                SELECT hodnota FROM nastaveni WHERE volba = 'verze'
                """)
            if vystup.fetchone()[0] != AKTUALNI_VERZE_DB:
                raise err.ChybaJinaVerzeDB("Databáze je v jiné verzi!")

        except sqlite.OperationalError, e:
            raise err.ChybaDB("Databáze není korektní! (%s)" % e)
        except TypeError, e:
            raise err.ChybaDB("Databáze není korektní! (%s)" % e)



    def vloz_klienta(self, jmeno, prijmeni, adresa="", telefon="", 
            mobil1="", mobil2="", pozn="", os=0, oa=0, km_os="0", os_pausal="0", os_cena_do="0", os_cena_mezi="0", os_cena_nad="0", os_pausalHodin="0"):
        """Vložení nového klienta do databáze.
            Požadované údaje jsou jméno a příjmení"""
        if jmeno == "":
            raise err.ChybaPrazdnePole("Není zadáno žádné jméno!")
        if prijmeni == "":
            raise err.ChybaPrazdnePole("Není zadáno žádné příjmení!")
        try:
            self.databaze.execute("""INSERT INTO 
                klienti (jmeno, prijmeni, adresa, telefon, mobil1, mobil2, pozn, os, oa, km_os, os_pausal, os_cena_do, os_cena_mezi, os_cena_nad, os_pausalHodin)
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)""",
                (jmeno, prijmeni, adresa, telefon, mobil1, mobil2, pozn, os, oa, km_os, os_pausal, os_cena_do, os_cena_mezi, os_cena_nad,os_pausalHodin))
        except sqlite.Error, e:
            log(e)

    def zmen_klienta(self, id_klienta, jmeno, prijmeni, adresa="", telefon="", 
            mobil1="", mobil2="", pozn="", os=0, oa=0, km_os="", os_pausal="", os_cena_do="", os_cena_mezi="",  os_cena_nad="", os_pausalHodin=""):
        """Změna informací o klientovi"""
        if jmeno == "":
            raise err.ChybaPrazdnePole("Není zadáno žádné jméno!")
        if prijmeni == "":
            raise err.ChybaPrazdnePole("Není zadáno žádné příjmení!")
        try:
            self.databaze.execute("""UPDATE klienti 
                SET jmeno=?, prijmeni=?, adresa=?, telefon=?, mobil1=?, mobil2=?, pozn=?, os=?, oa=?, km_os=?, os_pausal=?, os_cena_do=?, os_cena_mezi=?, os_cena_nad=?, os_pausalHodin=?
                WHERE id_klienta=?""",
                (jmeno, prijmeni, adresa, telefon, mobil1, mobil2, pozn, os, oa, km_os, os_pausal, os_cena_do, os_cena_mezi, os_cena_nad, os_pausalHodin, id_klienta))
        except sqlite.Error, e:
            log(e)

    def smaz_klienta(self, id_klienta):
        try:
            self.databaze.execute("""DELETE FROM klienti 
                WHERE id_klienta=?""",(str(id_klienta),))
        except sqlite.Error, e:
            log(e)

    def klienti(self):
        """Vrácení všech klientů se všemi informacemi"""
        try:
            vysledek = self.databaze.execute("""SELECT
                id_klienta, jmeno, prijmeni, adresa, telefon, mobil1, mobil2, pozn, os, oa, km_os,  os_pausal, os_cena_do, os_cena_mezi, os_cena_nad, os_pausalHodin
                FROM klienti""")
            return vysledek.fetchall()
        except sqlite.Error, e:
            log(e)

    def klienti_id_jmeno(self,vystup=0, pouze=None,mesic=None,rok=None):
        """Vrátí slovník klientů s patřičným id
        proměnná vystup říká zda bude výstup v pořadí jmeno prijmeni (0) nebo prijmeni jmeno (1)"""
        klienti = {}
        try:
            if pouze == 'os':
                vysledek = self.databaze.execute("""SELECT
                    id_klienta, jmeno, prijmeni
                    FROM klienti WHERE os != '0' ORDER BY prijmeni""")
            elif pouze == 'oa':
                vysledek = self.databaze.execute("""SELECT
                    id_klienta, jmeno, prijmeni
                    FROM klienti WHERE oa = '0' ORDER BY prijmeni""")
            elif pouze == 'osz':
                vysledek = self.databaze.execute("""SELECT 
                    klienti.id_klienta, klienti.jmeno, klienti.prijmeni
                    FROM klienti, zaznamy_os 
                    WHERE klienti.id_klienta = zaznamy_os.id_klienta 
                        AND  strftime('%Y-%m', zaznamy_os.datum)=? 
                    GROUP BY klienti.id_klienta""",
                    (str(rok) + "-" + str(mesic),))
            else:
                vysledek = self.databaze.execute("""SELECT
                    id_klienta, jmeno, prijmeni
                    FROM klienti ORDER BY prijmeni""")
            vysledek = vysledek.fetchall()
            if vysledek:
                for id_klienta, jmeno, prijmeni in vysledek:
                    if vystup:
                        klienti[id_klienta] = prijmeni + " " + jmeno
                    else:
                        klienti[id_klienta] = jmeno + " " + prijmeni
            return klienti
        except sqlite.Error, e:
            log(e)
          


    def klient_podle_id(self, id_klienta):
        """Vrácení konkrétního klienta podle id"""
        try:
            vysledek = self.databaze.execute("""SELECT
                id_klienta, jmeno, prijmeni, adresa, telefon, mobil1, mobil2, pozn, os, oa, km_os, os_pausal, os_cena_do, os_cena_mezi, os_cena_nad, os_pausalHodin
                FROM klienti WHERE id_klienta=?""", (str(id_klienta),)) 
            return vysledek.fetchone()
        except sqlite.Error, e:
            log(e)

    def klient_jmeno_podle_id(self, id_klienta, vystup=0):
        """Vrácení jméno klienta podle id,
        proměnná vystup říká zda bude výstup v pořadí jmeno prijmeni (0) nebo prijmeni jmeno (1)"""        
        try:
            vysledek = self.databaze.execute("""SELECT
                jmeno, prijmeni
                FROM klienti WHERE id_klienta=?""", (str(id_klienta),)) 
            vysledek = vysledek.fetchone()
            if not vysledek:
                return ""
            if vystup:
                return vysledek[1] + " " + vysledek[0]
            else:
                return vysledek[0] + " " + vysledek[1]
        except sqlite.Error, e:
            log(e)

    def klient_id_podle_jmena(self, klient):
        """Vyhledání id klienta podle jména"""
        try:
            vysledek = self.databaze.execute("""SELECT
                id_klienta FROM klienti
                WHERE spoj(prijmeni, jmeno)=?""",(klient,))
            vysledek = vysledek.fetchone()
            if not vysledek:
                vysledek = self.databaze.execute("""SELECT
                id_klienta FROM klienti
                WHERE spoj(jmeno, prijmeni)=?""", (klient,))
                vysledek = vysledek.fetchone()
            if not vysledek:
                return None
            else:
                return vysledek[0]

#        except sqlite.Error, e:
        except err.ChybaSoubor, e:
            log(e)

    def ceny_os_pro_klienta(self,id_klienta):
        """Vyhledání cen os pro konkrétního klienta"""
        try:
            vysledek = self.databaze.execute("""SELECT os_pausal, os_cena_do, os_cena_mezi, os_cena_nad, os_pausalHodin
                FROM klienti WHERE id_klienta=?""", (str(id_klienta),))
            return vysledek.fetchone()
        except sqlite.Error, e:
            log(e)
        

    def vloz_zaznam_os(self, id_klienta, datum, cas_od, cas_do, dovoz, odvoz):
        """Zadání záznamu pro osobní asistenci (os)"""
        if id_klienta == "":
            raise err.ChybaPrazdnePole("Není zadáno žádné id_klienta!")
        if datum == "":
            raise err.ChybaPrazdnePole("Není zadáno žádné datum!")
        if cas_od== "":
            raise err.ChybaPrazdnePole("Není zadán cas_od!")
        if cas_do== "":
            raise err.ChybaPrazdnePole("Není zadán cas_do!")
        if dovoz == "":
            raise err.ChybaPrazdnePole("Není zadán dovoz!")
        if odvoz == "":
            raise err.ChybaPrazdnePole("Není zadán odvoz!")
        try:
            self.databaze.execute("""INSERT INTO 
                zaznamy_os (id_klienta, datum, cas_od, cas_do, dovoz, odvoz)
                values (?, ?, ?, ?, ?, ?)""",
                (id_klienta, datum, cas_od, cas_do, dovoz, odvoz))
        except sqlite.Error, e:
            log(e)

    def zmen_zaznam_os(self, id_klienta, datum, cas_od, cas_do, dovoz, odvoz, id_zaznamu):
        """Změna záznamu pro osobní asistenci (os) podle id_zaznamu (id)"""
        if id_klienta == "":
            raise err.ChybaPrazdnePole("Není zadáno žádné id_klienta!")
        if datum == "":
            raise err.ChybaPrazdnePole("Není zadáno žádné datum!")
        if cas_od== "":
            raise err.ChybaPrazdnePole("Není zadán cas_od!")
        if cas_do== "":
            raise err.ChybaPrazdnePole("Není zadán cas_do!")
        if dovoz == "":
            raise err.ChybaPrazdnePole("Není zadán dovoz!")
        if odvoz == "":
            raise err.ChybaPrazdnePole("Není zadán odvoz!")
        try:
            self.databaze.execute("""UPDATE zaznamy_os 
                SET id_klienta=?, datum=?, cas_od=?, cas_do=?, dovoz=?, odvoz=?
                WHERE id=?""",
                (id_klienta, datum, cas_od, cas_do, dovoz, odvoz, id_zaznamu))
        except sqlite.Error, e:
            log(e)

    def smaz_zaznam_os(self, id_zaznamu):
        """Smazání záznamu os podle id_zaznamu"""
        try:
            self.databaze.execute("""DELETE FROM zaznamy_os
                WHERE id=?""", (str(id_zaznamu),))
        except sqlite.Error, e:
            log(e)
    
    def vypis_zaznamy_os(self, zaznam_id=None, id_klienta=None, datum=None, 
            mesic=None, rok=None, razeni=None, limit=None):
        """Výpis záznamů odlehčovací služby podle různých kritérií"""
        #výpis konkrétního záznamu podle id
        if zaznam_id:
            try:
                vysledek = self.databaze.execute("""SELECT
                    id, id_klienta, datum, cas_od, cas_do, dovoz, odvoz
                    FROM zaznamy_os WHERE id=?""", (str(zaznam_id),))
                return vysledek.fetchone()
            except sqlite.Error, e:
                log(e)
        
        w = " WHERE "
        where_data = []
        where_pouzito = False
        if id_klienta:
            w += " id_klienta=? "
            where_data.append(id_klienta)
            where_pouzito = True
        if datum:
            if where_pouzito:
                w += " AND "
            w += " datum=? "
            where_data.append(datum)
            where_pouzito = True
        elif mesic:
            if where_pouzito:
                w += " AND "
            if not rok:
                rok = time.strftime('%Y')
            w += " strftime('%Y-%m', datum)=? "
            where_data.append(str(rok) + "-" + str(mesic))
            where_pouzito = True

        o = " ORDER BY "
        order_pouzito = False
        if razeni == 'klient':
            o += " id_klienta ASC "
            order_pouzito = True
        elif razeni == 'datum':
            o += " datum ASC"
            order_pouzito = True

        l = ""
        if limit:
            l = " LIMIT " + str(int(limit))

        try:
            if not where_pouzito:
                w=""
            if not order_pouzito:
                o=""
#            log("""SELECT \
#                id, id_klienta, datum, cas_od, cas_do, dovoz, odvoz \
#                FROM zaznamy_os""" + w + o + l + str(where_data))
            vysledek = self.databaze.execute("""SELECT
                id, id_klienta, datum, cas_od, cas_do, dovoz, odvoz
                FROM zaznamy_os""" + w + o + l, where_data)
                
            return vysledek.fetchall()
#        except sqlite.Error, e:
        except err.ChybaSoubor, e:
            log(e)

    def zaznamy_pouzite_roky(self):
        """vrátí jednotlivé roky které jsou použity v záznamech os"""
        try:
            vysledek = self.databaze.execute("""SELECT strftime('%Y', datum) AS rok 
                    FROM zaznamy_os GROUP BY rok""")
            return vysledek.fetchall()
        except sqlite.Error, e:
            log(e)

    def existuje_podobny_zaznam(self, klient, datum):
        """Zjištění existence podobného záznamu v db (stejný datum a klient)"""
        try:
            vysledek = self.databaze.execute("""SELECT id, id_klienta, datum FROM zaznamy_os 
                    WHERE id_klienta=? AND datum=?""", (klient,datum))
            if vysledek.fetchall():
                return True
            else:
                return False
        except sqlite.Error, e:
            log(e)


    def nastaveni(self, volba=None):
        """Výpis veškerého nastavení (případně jen jedné volby)"""
        if volba:
            try:
                vysledek = self.databaze.execute(
                        """SELECT volba, hodnota, pozn FROM nastaveni WHERE volba=:volba""",{'volba' : volba})
                return vysledek.fetchone()
            except sqlite.Error, e:
                log(e)
        else:
            try:
                vysledek = self.databaze.execute("""SELECT
                    volba, hodnota, pozn
                    FROM nastaveni""") 
                return vysledek.fetchall()
            except sqlite.Error, e:
                log(e)

    def nastaveni_slovnik(self):
        tmp_nastaveni = self.nastaveni()
        tmp_nastaveni_slovnik = {}
        for volba, hodnota, pozn in tmp_nastaveni:
            tmp_nastaveni_slovnik[volba] = [hodnota, pozn]
        return tmp_nastaveni_slovnik

    def zmen_nastaveni(self, volba, hodnota, pozn=None):
        """Změna nastavení jednotlivých voleb"""
        try:
            if pozn:
                self.databaze.execute("""UPDATE nastaveni
                    SET hodnota=?, pozn=? WHERE volba=?""",(hodnota, pozn, volba))
            else:
                self.databaze.execute("""UPDATE nastaveni SET hodnota=? WHERE volba=?""", (hodnota, volba))
        except sqlite.Error, e:
            log(e)


    def commit(self):
        """Uložení změn do databáze"""
        self.databaze.commit()


def aktualizace_db_na_novejsi_verzi(soubor):
    """Provede aktualizaci databáze na novější verzi (pokud je to možné)"""
    try:
        db = sqlite.connect(soubor)
        db.text_factory = lambda x: unicode(x, "utf-8", "ignore")
        db.create_function('spoj', 2, spoj_s_mezerou)
    except sqlite.OperationalError, e:
        raise err.ChybaSoubor("Nemohu otevřít soubor %s! (%s)" % (soubor,e))
    try:
        stara_verze_db = int(db.execute("""
                SELECT hodnota FROM nastaveni WHERE volba = 'verze'
                """).fetchone()[0])
    except sqlite.OperationalError, e:
        raise err.ChybaDB("Databáze není korektní! (%s)" % e)
    except TypeError, e:
        raise err.ChybaDB("Databáze není korektní! (%s)" % e)        

    if stara_verze_db < int(AKTUALNI_VERZE_DB):
        if stara_verze_db < 1:
            # aktualizace z verze 0 na verzi 1
            # přidání sloupců os_pausal, os_cena_do a os_cena_nad do tabulky klienti
            db.execute("""ALTER TABLE klienti ADD COLUMN os_pausal INTEGER ;""")
            db.execute("""ALTER TABLE klienti ADD COLUMN os_cena_do INTEGER ;""")
            db.execute("""ALTER TABLE klienti ADD COLUMN os_cena_nad INTEGER ;""")
            # uklizení
            cena_os_do_60h = db.execute("""SELECT hodnota FROM nastaveni WHERE volba=?""",('cena_os_do_60h',)).fetchone()[0]
            cena_os_nad_60h = db.execute("""SELECT hodnota FROM nastaveni WHERE volba=?""",('cena_os_nad_60h',)).fetchone()[0]
            db.execute("""UPDATE klienti SET os_pausal='0', os_cena_do=?, os_cena_nad=? """,(cena_os_do_60h,cena_os_nad_60h))
            db.execute("""DELETE FROM nastaveni WHERE volba=?""",("cena_os_do_60h",))
            db.execute("""DELETE FROM nastaveni WHERE volba=?""",("cena_os_nad_60h",))
            
            
            # nastavení správného čísla aktuální verze
            db.execute("""UPDATE nastaveni SET hodnota=? WHERE volba=?""", (1, "verze"))
            db.commit()

            # další kontrola verze db
            aktualizace_db_na_novejsi_verzi(soubor)

        elif stara_verze_db < 2:
            # aktualizace z verze 1 na verzi 2
            # přidání položky vystavil do nastavení
            db.execute("""INSERT INTO nastaveni (volba, hodnota, pozn)
                    values (?,?,?)""", ('vystavil', '', 'Vystavil'))
            # nastavení správného čísla aktuální verze
            db.execute("""UPDATE nastaveni SET hodnota=? WHERE volba=?""", (2, "verze"))
            db.commit()

            # další kontrola verze db
            aktualizace_db_na_novejsi_verzi(soubor)

        elif stara_verze_db < 3:
            # aktualizace z verze 2 na verzi 3
            # přidání položky ḱod_stala_cast a kod_promenna_cast do nastavení
            db.execute("""INSERT INTO nastaveni (volba, hodnota, pozn)
                    values (?,?,?)""", ('kod_stala_cast', 'XXXX', 'Kód faktury (stálá část)'))
            db.execute("""INSERT INTO nastaveni (volba, hodnota, pozn)
                    values (?,?,?)""", ('kod_promenna_cast', '0000', 'Kód faktury (proměnná část)'))
            # nastavení správného čísla aktuální verze
            db.execute("""UPDATE nastaveni SET hodnota=? WHERE volba=?""", (3, "verze"))
            db.commit()

            # další kontrola verze db
            aktualizace_db_na_novejsi_verzi(soubor)


        elif stara_verze_db < 4:
            # aktualizace z verze 3 na verzi 4
            # přidání položek dolni_hranice_poctu_hodin, horni_hranice_poctu_hodin, adresa a adresa_dalsi do nastaveni
            nastaveni = (('dolni_hranice_poctu_hodin','30','Dolní hranice pro počet hodin OS'),
                        ('horni_hranice_poctu_hodin','60','Horní hranice pro počet hodin OS'),
                        ('adresa','Občanské sdružení BENEDIKTUS|Klášterní 60|583 01 Chotěboř','Adresa uváděná v sestavách'),
                        ('adresa_dalsi','IČ: 70868832|DIČ: CZ70868832|Mobil: +420 731 646 811|E-mail: benediktus@centrum.cz|WWW: benediktus.infobar.cz','Doplňující informace v adrese'))
            for t in nastaveni:
                db.execute("""INSERT INTO nastaveni (volba, hodnota, pozn)
                    values (?, ?, ?)""", t)
 
            # přidání sloupce os_cena_mezi ke klientum
            db.execute("""ALTER TABLE klienti ADD COLUMN os_cena_mezi INTEGER ;""")


            # nastavení správného čísla aktuální verze
            db.execute("""UPDATE nastaveni SET hodnota=? WHERE volba=?""", (4, "verze"))
            db.commit()

            # další kontrola verze db
            aktualizace_db_na_novejsi_verzi(soubor)


        elif stara_verze_db < 5:
            # aktualizace z verze 4 na verzi 5
            # přidání sloupce os_pausalHodin do tabulky klienti
            db.execute("""ALTER TABLE klienti ADD COLUMN os_pausalHodin INTEGER ;""")
            # uklizení
            db.execute("""UPDATE klienti SET os_pausalHodin='0'""")
            
            
            # nastavení správného čísla aktuální verze
            db.execute("""UPDATE nastaveni SET hodnota=? WHERE volba=?""", (5, "verze"))
            db.commit()

            # další kontrola verze db
            aktualizace_db_na_novejsi_verzi(soubor)




def vyprazdneni_zaznamu_z_db(soubor):
    """Provede odstranění záznamů (os) z databáze (ostatní data v ní zůstanou)"""
    try:
        db = sqlite.connect(soubor)
#        db.text_factory = lambda x: unicode(x, "utf-8", "ignore")
    except sqlite.OperationalError, e:
        raise err.ChybaSoubor("Nemohu otevřít soubor %s! (%s)" % (soubor,e))
    
    db.execute("""DELETE FROM zaznamy_os""")
    db.commit()



   
def spoj_s_mezerou(a, b):
    """spojí řetězce 'a' a 'b' mezerou"""
    return str(a) + " " + str(b)



    
    





def test():
    print "Otestování funkčnosti modulu benedat_sqlite.py."
    print "Jako parametr se zadává název souboru."
    print "Při zadání názvu neexistujícího souboru dojde k pokusu o vytvoření db s tímto názvem."
    print "Při zadání názvu existujícího souboru dojde k pokusu o otevření souboru jako db a kontrole db."
    print "===============================================\n"
    try:
        if len(sys.argv) > 1:
            db = Db(sys.argv[1])
#   Vložení nových klientů
#            db.vloz_klienta("Matouš", "Sedláček")
#            db.vloz_klienta("Martin", "Janeček")
#            db.vloz_klienta("Alexandr", "Bouček")

#   Změna informací klienta
#            db.zmen_klienta(1, "Jan", "Ladislav", os=1)

#   Vypsání existujících klientů
#            for klient in db.klienti():
#                for polozka in klient:
#                    print polozka, "\t",
#                print

#   Vypsání klienta podle id
#            klient = db.klient_podle_id(8)
#            if klient:
#                for polozka in klient:
#                    print polozka, "\t",
#                print

#   Vypsání jména klienta podle id
#            print db.klient_jmeno_podle_id(3,1)

#   Vypsání slovníku klíč: id_klienta, jméno a příjmení hodnota
#            klienti = db.klienti_id_jmeno(1)
#            for klic in klienti.keys():
#                print str(klic) + ":", klienti[klic]


#   Zadání zaznamu_os
#            db.vloz_zaznam_os(2, '2009-06-22', '9:15', '15:45', 0, 1)

#   Změna záznamu_os
#            db.zmen_zaznam_os(1, '2009-06-11', '11:00', '11:30', 1, 0, 6)

#   Výpis záznamů_os
#            for zaznam in db.vypis_zaznamy_os():
#                for polozka in zaznam: 
#                    print polozka, "\t",
#                print

#   Výpis záznamu_os podle id
#            zaznam = db.vypis_zaznamy_os(zaznam_id=4)
#            if zaznam:
#                for polozka in zaznam:
#                    print polozka, "\t",
#                print

#   Výpis záznamů_os podle různých kritérií
#            zaznamy = db.vypis_zaznamy_os(razeni='datum', limit='3')
#            if zaznamy: 
#                for zaznam in zaznamy:
#                    for polozka in  zaznam:
#                        print polozka, "\t",
#                    print

#   Výpis nastavení
#            zaznamy = db.nastaveni()
#            if zaznamy:
#                for zaznam in zaznamy:
#                    for polozka in zaznam:
#                        print polozka, "\t",
#                    print
#            zaznam = db.nastaveni("cestovne_os_nastupni_sazba")
#            zaznam = db.nastaveni("verze")
#            if zaznam:
#                for polozka in zaznam:
#                    print polozka, "\t",
#                print

#   Změna nastavení
#            db.zmen_nastaveni("verze", "0.1")



            print db.nastaveni_slovnik()

            db.databaze.commit()
    except err.ChybaSoubor, e:
        print "CHYBA:",
        print e



if __name__ == "__main__":
    test()


