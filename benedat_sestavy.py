#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""Modul pro generování přehledů a sestav"""

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
import os
import string
import getopt
import time

import benedat_pdf as bpdf
import benedat_sqlite as bsqlite
import benedat_export_Pohoda as bpohoda
import benedat_cas as bcas
import benedat_export_csv as bcsv

DEBUG = False
#DEBUG = True

class Sestavy():
    """Třída pro generování sestav"""

    def __init__(self, db):
        self.db = db


    def sestava(self, id_klienta, mesic, rok):
        """vygenerování sestavy pro určitého klienta za určité období"""
        # data o klientovi
        #0           1      2         3       4        5       6       7     8   9   10     11         12          13            14           15              16 
        #id_klienta, jmeno, prijmeni, adresa, telefon, mobil1, mobil2, pozn, os, oa, km_os, os_pausal, os_cena_do, os_cena_mezi, os_cena_nad, os_pausalHodin, typ_dokladu
        data_klient = self.db.klient_podle_id(id_klienta)

        # data záznamů os
        data_zaznamy_z_db = self.db.vypis_zaznamy_os(id_klienta = id_klienta, 
                mesic = mesic, rok = rok, 
                razeni='datum')
        data_zaznamy = []
        for z in data_zaznamy_z_db:
            zaznam = [z[2], z[3], z[4], rozdil_casu(z[3], z[4]), z[5], z[6], z[7]]
            data_zaznamy.append(zaznam)
        
        # souhrn [pocet_hodin, cena_os, pocet_cest, cena_cest, pocet_prenocovani, cena_prenocovani, celkem]
        data_souhrn = [0,0,0,0,0,0,0]
        for z in data_zaznamy:
            data_souhrn[0] += z[3]  # počet hodin
            data_souhrn[2] += z[4] + z[5] # počet cest
            data_souhrn[4] += z[6] # počet přenocování
        # cena os
        data_souhrn[1] = self.cena_os(data_souhrn[0], id_klienta)
        data_souhrn[3] = data_souhrn[2] * self.cena_cesty(id_klienta)
        data_souhrn[5] = data_souhrn[4] * int(self.db.nastaveni('os_cena_prenocovani')[1])
        # celková cena (zaokrouhlená na koruny)
        data_souhrn[6] = round(data_souhrn[1] + data_souhrn[3] + data_souhrn[5], 0)

        # data_dalsi [dovoz, odvoz]
        data_dalsi = [0, 0]
        for z in data_zaznamy:
            data_dalsi[0] += z[4]
            data_dalsi[1] += z[5]

        return data_klient, data_zaznamy, data_souhrn, data_dalsi


    def cena_cesty(self, id_klienta):
        """výpočet ceny jedné cesty klienta"""
    # km (vzdálenost z domu do domečku) se zaokrouhlí nahoru na sudé celé číslo - tarifní km podle ceníku. dále:
    # kč za cestu = nástupní sazba + podíl klienta*( k/100 * cena za litr * (tarifní délka)^exp )  
    # , zaokrouhlit na celé kč
    # konstanty:
    # nástupní sazba = 6 kč
    # k = 15
    # exp = 0,85
    # podíl klienta = 0,5
    # cena za litr = 33 kč 

        # získání vzdálenosti z databáze
        vzdalenost_km = self.db.klient_podle_id(id_klienta)[10]
        if vzdalenost_km == None:
            vzdalenost_km = 0
        # zaokrouhlení na vyšší sudé číslo
#        print  vzdalenost_km
        if vzdalenost_km % 2:
            vzdalenost_km += 1
#        print  vzdalenost_km
        # získání dalších údajů z db (nastavení)
        cestovne_os_cena_za_litr = float(self.db.nastaveni('cestovne_os_cena_za_litr')[1])
#        print cestovne_os_cena_za_litr
        cestovne_os_exp = float(self.db.nastaveni('cestovne_os_exp')[1])
#        print cestovne_os_exp
        cestovne_os_k = float(self.db.nastaveni('cestovne_os_k')[1])
#        print cestovne_os_k
        cestovne_os_nastupni_sazba = float(self.db.nastaveni('cestovne_os_nastupni_sazba')[1])
#        print cestovne_os_nastupni_sazba
        cestovne_os_podil_klienta = float(self.db.nastaveni('cestovne_os_podil_klienta')[1])
#        print cestovne_os_podil_klienta

        cena = cestovne_os_nastupni_sazba + cestovne_os_podil_klienta * \
            (cestovne_os_k / 100.0 * \
            cestovne_os_cena_za_litr * \
            (vzdalenost_km ** cestovne_os_exp))
            
#        print "========================"
#        print cena
        
        # zaokrouhlení ceny
        cena = round(cena, 0)
#        print cena
#        print 

        return cena

    def cena_os(self, pocet_hodin, id_klienta):
        """výpočet celkové ceny za os"""
        pocet_hodin = float(pocet_hodin)
        (os_pausal, os_cena_do, os_cena_mezi, os_cena_nad, os_pausalHodin) = self.db.ceny_os_pro_klienta(id_klienta)
        os_pausal = float(os_pausal)
        os_cena_do = float(os_cena_do)
        os_cena_mezi = float(os_cena_mezi)
        os_cena_nad = float(os_cena_nad)
        os_pausalHodin = float(os_pausalHodin)
        
        dolni_hranice_poctu_hodin = int(self.db.nastaveni('dolni_hranice_poctu_hodin')[1])
        horni_hranice_poctu_hodin = int(self.db.nastaveni('horni_hranice_poctu_hodin')[1])
        
        # výpočet aktuálního paušálu (v případě méně hodin než polovinu předpokládaného 
        # počtu se započítá jen polovina paušálu
        if pocet_hodin < (os_pausalHodin/2):
            aktualni_os_pausal = os_pausal / 2
        else :
            aktualni_os_pausal = os_pausal

        if pocet_hodin > horni_hranice_poctu_hodin:
            cena = aktualni_os_pausal + (os_cena_nad *  (pocet_hodin - horni_hranice_poctu_hodin)) + \
                               (os_cena_mezi * (horni_hranice_poctu_hodin - dolni_hranice_poctu_hodin)) + \
                               (os_cena_do *   (dolni_hranice_poctu_hodin))
        elif pocet_hodin > dolni_hranice_poctu_hodin:
            cena = aktualni_os_pausal + (os_cena_mezi * (pocet_hodin - dolni_hranice_poctu_hodin)) + \
                               (os_cena_do *   (dolni_hranice_poctu_hodin))
        else:
            cena = aktualni_os_pausal + os_cena_do * pocet_hodin
        return round(cena, 2)
        



    def sestava_text(self, id_klienta, mesic, rok):
        """vygenerování sestavy do textu"""
        data_klient, data_zaznamy, data_souhrn, data_dalsi= self.sestava(id_klienta, mesic, rok)
        tmp = ""
        tmp += data_klient[1] + " " + data_klient[2] + "\n"
        tmp += str(data_klient[3]) + "\n"

        tmp += "datum\t\tcas od\tcas do\tcelkem\tdovoz\todvoz\n"
        for r in data_zaznamy:
            tmp += r[0] + "\t" + r[1] + "\t" + r[2] + "\t" + str(r[3]) + "\t" + str(r[4]) + "\t" + str(r[5]) + "\n"
        tmp += "celkem hodin:\t"
        tmp += str(data_souhrn[0])
        tmp += "\n"
        tmp += "Cena: OS\t"
        tmp += str(data_souhrn[1])
        tmp += " kc"
        tmp += "\n"
        tmp += "Celkem cest: \t"
        tmp += str(data_souhrn[2])
        tmp += "\n"
        tmp += "Cena za cesty:\t"
        tmp += str(data_souhrn[3])
        tmp += " kc"
        tmp += "\n"
        tmp += "Cena celkem\t"
        tmp += str(data_souhrn[4])
        tmp += " kc"
        tmp += ""
        
        return tmp

    def cast_sestavy_pdf(self,s , id_klienta, mesic, rok, datum_vystaveni="", datum_platby="", vystavil="", typ_dokladu=0):
        """Vytvoření obsahu jedné sestavy"""
        # získání dat do sestavy
        data_klient, data_zaznamy, data_souhrn, data_dalsi = self.sestava(id_klienta, mesic, rok)
        # kód sestavy
        kod_stala_cast = str(self.db.nastaveni(volba="kod_stala_cast")[1])
        kod_promenna_cast = str(self.db.nastaveni(volba="kod_promenna_cast")[1])
        kod = kod_stala_cast + kod_promenna_cast
        # název pokladny
        pokladna = str(self.db.nastaveni(volba="pokladna")[1])
        
        # vyplnění sestavy
        s.typ_dokladu(typ_dokladu)
        s.adresa_l((self.db.nastaveni('adresa')[1],))
        s.adresa_l_dalsi((self.db.nastaveni('adresa_dalsi')[1],))
        s.adresa_r((data_klient[1] + " " + data_klient[2], data_klient[3]))
        s.datum_vystaveni(datum_vystaveni)
        if typ_dokladu ==0:
            s.datum_platby(datum_platby)
            s.pokladna(pokladna)
        s.zaznamy(data_zaznamy)
        s.souhrn(data_souhrn)
        s.vystavil(vystavil)
        if typ_dokladu ==0:
            s.kod(kod)
        souhrnny_text = u"Účtujeme Vám za odlehčovací službu - " + str(mesic) + "/" + str(rok) + "."
#        souhrnny_text = "Účtujeme Vám za odlehčovací službu." 
        s.souhrnny_text(souhrnny_text)
        
        # vytvoření sestavy
        s.vytvor_sestavu()

        # vyplnění souhrnu pro účetnictví
#        self.souhrn_ucetnictvi[kod] = bpohoda.Souhrn_polozka()
#        su = self.souhrn_ucetnictvi[kod]
#        su.kod_stala_cast = kod_stala_cast
#        su.kod_promenna_cast = kod_promenna_cast
#        su.datum_vystaveni = datum_vystaveni
#        su.platce = data_klient[1] + " " + data_klient[2]
#        su.text = souhrnny_text
#        su.cena = data_souhrn[4]
        
        if typ_dokladu == 0:
            # Vyplnění dat do xml pro Pohodu
            self.xml_to_pohoda.pridani_dokladu(id=kod, id_dokladu=kod_promenna_cast,
                kod_promenna_cast=kod_promenna_cast, kod_stala_cast=kod_stala_cast,
                datum_vystaveni=bcas.preved_datum(datum_vystaveni,2), datum_platby=bcas.preved_datum(datum_platby,2),
                text=souhrnny_text,
                jmeno=data_klient[1] + " " + data_klient[2], adresa=data_klient[3],
                cena=str(data_souhrn[6]))

        # Vyplnění dat do csv
#        print kod
#        print kod_promenna_cast
#        print kod_stala_cast
#        print datum_vystaveni
#        print datum_platby
#        print souhrnny_text
#        print data_klient
#        print data_souhrn
#        print data_dalsi
        #"Příjmení", "Jméno", "Období", "Kód dokladu", "Počet hodin OS", "Cena za OS", 
        # "Dovozů", "Odvozů", "Cest celkem", "Cena za cesty", "Cena celkem",
        # "Vzdálenost v km", "OS paušál", "OS paušál hodin", "OS cena do", "OS cena mezi", "OS cena nad", "OS dolní hranice počtu hodin", "OS horní hranice počtu hodin", "Cena za litr"
        dolni_hranice_poctu_hodin = int(self.db.nastaveni('dolni_hranice_poctu_hodin')[1])
        horni_hranice_poctu_hodin = int(self.db.nastaveni('horni_hranice_poctu_hodin')[1])
        cestovne_os_cena_za_litr = float(self.db.nastaveni('cestovne_os_cena_za_litr')[1])
        self.csv.zapis_radek((data_klient[1], data_klient[2], str(mesic)+"/"+str(rok), kod, data_souhrn[0], data_souhrn[1],
            data_dalsi[0], data_dalsi[1], data_souhrn[2], data_souhrn[3],
            data_souhrn[4], data_souhrn[5], data_souhrn[6], 
            data_klient[10], data_klient[11], data_klient[15], data_klient[12], data_klient[13], data_klient[14], dolni_hranice_poctu_hodin, horni_hranice_poctu_hodin, cestovne_os_cena_za_litr))


        
        # aktualizace kódu
        if typ_dokladu ==0: 
            kod_promenna_cast = str(int(kod_promenna_cast) + 1).rjust(4, '0')
            self.db.zmen_nastaveni(volba="kod_promenna_cast", hodnota=kod_promenna_cast)
            self.db.commit()

        

    def sestava_pdf(self, id_klienta, mesic, rok, soubor,datum_vystaveni="",datum_platby="", vystavil=""):
        """Kompletní vytvoření jedné sestavy"""
        # soubor pro sestavu
        s = bpdf.Sestava(soubor=soubor)

        # soubor pro souhrn ucetnictvi
#        self.souhrn_ucetnictvi = bpohoda.Souhrn_ucetnictvi(soubor=soubor[:-3] + "txt")

        # xml pro Pohodu
        self.xml_to_pohoda = bpohoda.xmlDokument(id=str(mesic)+"_"+str(rok))

        # EXPORT DO CSV
        self.csv = bcsv.Souhrn_csv(soubor=soubor[:-3]+"csv")
        # názvy sloupců
        self.csv.zapis_radek(("Příjmení", "Jméno", "Období", "Kód dokladu", "Počet hodin OS", "Cena za OS", 
                             "Dovozů", "Odvozů", "Cest celkem", "Cena za cesty",
                             "Přenocování", "Cena za přenocování", "Cena celkem",
                             "Vzdálenost v km", "OS paušál", "OS paušál hodin", "OS cena do", 
                             "OS cena mezi", "OS cena nad", "OS dolní hranice počtu hodin", 
                             "OS horní hranice počtu hodin", "Cena za litr"))
        
        # vyplnění sestavy
        self.cast_sestavy_pdf(s, id_klienta, mesic, rok,datum_vystaveni=datum_vystaveni,datum_platby=datum_platby,vystavil=vystavil)
        # vytvoření sestavy
        s.finalize()

#        self.souhrn_ucetnictvi.uloz()

        # xml pro Pohodu
        self.xml_to_pohoda.to_xml_soubor(soubor=soubor[:-3] + "xml", debug=DEBUG)


        # export do csv
        self.csv.close()

    def sestavy_pdf(self, mesic, rok, soubor,datum_vystaveni="",datum_platby="", vystavil=""):
        """Kompletní vytvoření více sestav do jednoho souboru"""
        # soubor pro sestavu
        s = bpdf.Sestava(soubor=soubor)

        # soubor pro souhrn ucetnictvi
#        self.souhrn_ucetnictvi = bpohoda.Souhrn_ucetnictvi(soubor=soubor[:-3] + "txt")

        # xml pro Pohodu
        self.xml_to_pohoda = bpohoda.xmlDokument(id=str(mesic)+"_"+str(rok))

        # EXPORT DO CSV
        self.csv = bcsv.Souhrn_csv(soubor=soubor[:-3]+"csv")
        # názvy sloupců
        self.csv.zapis_radek(("Příjmení", "Jméno", "Období", "Kód dokladu", "Počet hodin OS", "Cena za OS", 
                             "Dovozů", "Odvozů", "Cest celkem", "Cena za cesty",
                             "Přenocování", "Cena za přenocování", "Cena celkem",
                             "Vzdálenost v km", "OS paušál", "OS paušál hodin", "OS cena do", 
                             "OS cena mezi", "OS cena nad", "OS dolní hranice počtu hodin", 
                             "OS horní hranice počtu hodin", "Cena za litr"))



        # kterých klientů se to týká
        klienti = self.db.klienti_id_jmeno(1, pouze='osz', 
            mesic=mesic, rok=rok)
        # projití klientů a vyplnění sestavy pro kažedého klienta
        for klient in klienti.keys():
            self.cast_sestavy_pdf(s, klient, mesic, rok,datum_vystaveni=datum_vystaveni,datum_platby=datum_platby, vystavil=vystavil)
        # vytvoření sestavy
        s.finalize()

#        self.souhrn_ucetnictvi.uloz()

        # xml pro Pohodu
        self.xml_to_pohoda.to_xml_soubor(soubor=soubor[:-3] + "xml", debug=DEBUG)


        # export do csv
        self.csv.close()

      
    def sestavy_vyber_pdf(self, klienti, mesic, rok, soubor,datum_vystaveni="",datum_platby="", vystavil="", typ_dokladu=0):
        """Kompletní vytvoření více sestav do jednoho souboru"""
        # soubor pro sestavu
        s = bpdf.Sestava(soubor=soubor)

        # soubor pro souhrn ucetnictvi
#        self.souhrn_ucetnictvi = bpohoda.Souhrn_ucetnictvi(soubor=soubor[:-3] + "txt")

        # xml pro Pohodu
        if typ_dokladu==0:
            self.xml_to_pohoda = bpohoda.xmlDokument(id=str(mesic)+"_"+str(rok))

        # EXPORT DO CSV
        self.csv = bcsv.Souhrn_csv(soubor=soubor[:-3]+"csv")
        # názvy sloupců
        self.csv.zapis_radek(("Příjmení", "Jméno", "Období", "Kód dokladu", "Počet hodin OS", "Cena za OS", 
                             "Dovozů", "Odvozů", "Cest celkem", "Cena za cesty",
                             "Přenocování", "Cena za přenocování", "Cena celkem",
                             "Vzdálenost v km", "OS paušál", "OS paušál hodin", "OS cena do", 
                             "OS cena mezi", "OS cena nad", "OS dolní hranice počtu hodin", 
                             "OS horní hranice počtu hodin", "Cena za litr"))



        # kterých klientů se to týká
#        klienti = self.db.klienti_id_jmeno(1, pouze='osz', 
#            mesic=mesic, rok=rok)
#        print klienti
        # projití klientů a vyplnění sestavy pro kažedého klienta
        for klient in klienti:
            self.cast_sestavy_pdf(s, klient, mesic, rok,datum_vystaveni=datum_vystaveni,datum_platby=datum_platby, vystavil=vystavil, typ_dokladu=typ_dokladu)
        # vytvoření sestavy
        s.finalize()

#        self.souhrn_ucetnictvi.uloz()

        # xml pro Pohodu
        if typ_dokladu==0:
            self.xml_to_pohoda.to_xml_soubor(soubor=soubor[:-3] + "xml", debug=DEBUG)


        # export do csv
        self.csv.close()

  
######
        






def rozdil_casu(cas_a, cas_b):
    """vypočítání rozdílu dvou časů zadaných jako řetězec"""
    h_cas_a, m_cas_a = string.split(cas_a, ':')
    h_cas_b, m_cas_b = string.split(cas_b, ':')
    
    h_cas_a = int(h_cas_a)
    h_cas_b = int(h_cas_b)
    m_cas_a = int(m_cas_a)
    m_cas_b = int(m_cas_b)

    if h_cas_a < h_cas_b:
        doba = h_cas_b - h_cas_a
        doba += (m_cas_b - m_cas_a) / 60.0
    else:
        doba = h_cas_a - h_cas_b
        doba += (m_cas_a - m_cas_b) / 60.0
    
    return doba






def test(db_soubor = None):
    """Testovací funkce"""
    if not db_soubor or not os.path.isfile(db_soubor):
        print """Testovací funkci musí být předán název existujícího souboru s databází!"""
        sys.exit(1)
    db = bsqlite.Db(db_soubor)

    sestava = Sestavy(db)
    print sestava.sestava('5', '07', '2009')
    print
#    print sestava.sestava_text('5', '07', '2009')
    sestava.sestava_pdf('5', '07', '2009',"test.pdf")
    
def main():
    if len(sys.argv)>1:
        #defaultní hodnoty
        db_soubor = None
        mesic = time.strftime('%m')
        rok = time.strftime('%Y')
        klient = -1
        vystupni_pdf = 'Sestava.pdf'
        datum_vystaveni = ""
        datum_platby = ""
        vystavil = ""
        
        # možné volby:
        # -d    databázový soubor
        # -m    měsíc
        # -r    rok
        # -k    klient
        # -o    výstupní soubor
        # -v    datum vystavení
        # -s    datum platby
        # -f    vystavil
        volby = 'd:m:r:k:o:v:p:f:'
        (volby, argumenty) = getopt.getopt(sys.argv[1:], volby)
        for volba,hodnota in volby:
            if volba == '-d':
                db_soubor = hodnota
            elif volba == '-m':
                mesic = hodnota
            elif volba == '-r':
                rok = hodnota
            elif volba == '-k':
                klient = hodnota
            elif volba == '-o':
                vystupni_pdf = hodnota
            elif volba == '-v':
                datum_vystaveni = hodnota
            elif volba == '-p':
                datum_platby = hodnota
            elif volba == '-f':
                vystavil = hodnota

        if not db_soubor or not os.path.isfile(db_soubor):
            print "Nebyl zadán existující databázový soubor!"
            return

        db = bsqlite.Db(db_soubor)

        sestava = Sestavy(db)
        if klient >= 0:
            # vytváříme sestavu pro jednoho klienta
            sestava.sestava_pdf(klient, mesic, rok, vystupni_pdf, datum_vystaveni=datum_vystaveni, datum_platby=datum_platby, vystavil=vystavil)
        else:
            # vytváříme sestavu pro více klientů
            sestava.sestavy_pdf(mesic, rok, vystupni_pdf, datum_vystaveni=datum_vystaveni, datum_platby=datum_platby, vystavil=vystavil)



    # rozdíly časů
#    rozdil_casu('09:00','15:00')
#    print
#    rozdil_casu('09:15','15:00')
#    print
#    rozdil_casu('09:45','15:00')
#    print
#    rozdil_casu('09:00','15:15')
#    print
#    print rozdil_casu('09:00','13:00')
#    print

if __name__ == "__main__":
    main()
#    test("database.db")
