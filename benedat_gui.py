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
    import gobject
    import pango
except:
    sys.exit(1)

import os
import shutil
import time
import re
import string
import locale
import subprocess
import unicodedata


import benedat_config as bconf
import benedat_sqlite as bsqlite
import benedat_chyby as berr
import benedat_cas as bcas
import benedat_sestavy as bsestavy
from benedat_log import *



class BenedatGladeFile:
    gladefile = ""
    def __init__(self):
        pass

class BenedatDB:
    db = None
    ulozeno = True
    db_soubor = None
    def __init__(self):
        pass

    def uloz_db(self):
        """Uložení změn do databáze."""
        BenedatDB.db.commit()
        BenedatDB.ulozeno = True




class BenedatHlavniOkno(BenedatGladeFile,BenedatDB):
    """Hlavní okno (rozcestník) aplikace Benedat"""


    def __init__(self, gladefile="benedat_gui.glade", konf=None):
        if konf:
            self.konf = konf
        else:
            self.konf = bconf.Konfigurace()
        BenedatGladeFile.gladefile = gladefile
#        __class__.gladefile = gladefile
        # načtení hlavního okna
        self.wHlavni = gtk.glade.XML(BenedatGladeFile.gladefile, "wHlavni")

        signaly = { 'on_wHlavni_destroy': self.konec,
                    'on_btNovaDB_clicked': self.dialog_nova_db,
                    'on_btOtevritDB_clicked': self.dialog_otevri_db,
                    'on_btUlozDb_clicked': self.on_btUlozDb_clicked,
                    'on_btZavriDb_clicked': self.nic,
                    'on_btEditaceZaznamuOS_clicked': self.on_btEditaceZaznamuOS_clicked,
                    'on_btSestavyOS_clicked': self.dialog_sestavy,
                    'on_btKlienti_clicked': self.klienti,
                    'on_btNastaveni_clicked': self.dialog_nastaveni,
                    'on_btExport_clicked': self.nic,
                    'on_btPrazdnaKopie_clicked': self.on_btPrazdnaKopie_clicked,
                    'on_btKonec_clicked': self.konec}
        self.wHlavni.signal_autoconnect(signaly)

        widgety = ('btNovaDB',
                    'btOtevritDB',
                    'btUlozDb',
                    'btZavriDb',
                    'btEditaceZaznamuOS',
                    'btSestavyOS',
                    'btKlienti',
                    'btNastaveni',
                    'btExport',
                    'btPrazdnaKopie',
                    'btKonec',
                    'sbHlavni'
                    )
        self.wHlavniWidgety = {}
        for w in widgety:
            self.wHlavniWidgety[w] = self.wHlavni.get_widget(w)
#            self.wHlavniWidgety[w] = gtk.glade.XML(BenedatGladeFile.gladefile, w).get_widget(w)

        # otevření minule otevřené databáze
        if self.konf.volba("otevreny_soubor"):
            self.databazovy_soubor = self.konf.volba("otevreny_soubor").decode("utf-8")
            if os.path.isfile(self.databazovy_soubor):
                self.otevreni_db()
            else:
                self.databazovy_soubor = ""
                BenedatDB.db_soubor = ""
                self.konf.volba("otevreny_soubor", self.databazovy_soubor)



    # funkce pro obsloužení volání tlačítek
    def nic(self, Widget, parametry=None):
        if parametry:
            print parametry

    def konec(self, widget):
        if not BenedatDB.ulozeno:
            navratova_hodnota = dialogDotaz(
                    text="Databáze nebyla uložena!", 
                    text_dalsi="Uložit databázi před zavřením programu?")
            if gtk.RESPONSE_YES == navratova_hodnota:
                BenedatDB.db.commit()
                BenedatDB.ulozeno = True
                gtk.main_quit()
            elif gtk.RESPONSE_NO == navratova_hodnota:
                gtk.main_quit()
            else:
                return
                
        else:
            gtk.main_quit()

    def dialog_nova_db(self, widget):
        # filtry pro zobrazované soubory
        filtr={}
        filtr['db'] = gtk.FileFilter()
        filtr['db'].add_pattern('*.db')
        filtr['vse'] = gtk.FileFilter()
        filtr['vse'].add_pattern('*')

        # změna filtru pro zobrazované soubory
        def cbNovaDBTypSouboru_changed(widget, data=None):
            if cbNovaDBTypSouboru.get_active() == 0:
                self.wNovaDB.set_filter(filtr['db'])
            else:
                self.wNovaDB.set_filter(filtr['vse'])



        # xml strom pro dialog
        xmlNovaDB = gtk.glade.XML(BenedatGladeFile.gladefile, "wNovaDB")
        self.wNovaDB = xmlNovaDB.get_widget("wNovaDB")
#        self.wNovaDB.connect('confirm-overwrite', on_wNovaDB_confirm_overwrite)
        # box pro výběr typu souboru
        cbNovaDBTypSouboru = xmlNovaDB.get_widget("cbNovaDBTypSouboru")
        # vyplnění boxu pro výběr souboru
        self.model_scrit = gtk.ListStore(str)
        self.model_scrit.append(["Pouze databázové soubory (*.db)"])
        self.model_scrit.append(["Všechny soubory"])
        cbNovaDBTypSouboru.set_model(self.model_scrit)
        cell = gtk.CellRendererText()
        cbNovaDBTypSouboru.pack_start(cell)
        cbNovaDBTypSouboru.add_attribute(cell,'text',0)
        cbNovaDBTypSouboru.set_active(0)
        # připojení signálu pro změnu
        cbNovaDBTypSouboru.connect('changed', cbNovaDBTypSouboru_changed)
        #nastavení výchozího filtru na db
        self.wNovaDB.set_filter(filtr['db'])
        
#        self.wNovaDB.set_do_overwrite_confirmation(True)

        navratova_hodnota = self.wNovaDB.run()
        
        # kontrola vybraného souboru
        if navratova_hodnota == gtk.RESPONSE_OK and self.wNovaDB.get_filename():
            soubor = self.wNovaDB.get_filename()
            if os.path.splitext(soubor)[1] != ".db":
                soubor += ".db"
            self.databazovy_soubor = soubor.decode("utf-8")
            BenedatDB.db_soubor = self.databazovy_soubor
            self.wNovaDB.destroy()
            self.vytvoreni_db()
        else:
            self.wNovaDB.destroy()

    def vytvoreni_db(self):
        """Vytvoření nové databáze"""
        try:
#            print "Byl vybrán soubor: %s" % self.databazovy_soubor
            BenedatDB.db = bsqlite.Db(self.databazovy_soubor, novy=True)
            self.konf.volba("otevreny_soubor", self.databazovy_soubor)
            self.povol_tlacitka_zavisla_na_db()
            self.nastav_statusbar("..." + self.databazovy_soubor[-30:])
        except berr.ChybaDB, e:
            dialogChyba(e)
            self.databazovy_soubor = None
            BenedatDB.db_soubor = self.databazovy_soubor
            self.konf.volba("otevreny_soubor", self.databazovy_soubor)
            self.zakaz_tlacitka_zavisla_na_db()
            self.nastav_statusbar("..." + self.databazovy_soubor[-30:])
           
    
    def on_btUlozDb_clicked(self, widget):
        """Obsloužení tlačítka pro uložení databáze"""
        self.uloz_db()

    def nastav_odkaz_na_konfiguraci(self, konf):
        self.konf = konf



    def dialog_otevri_db(self, widget):

        # filtry pro zobrazované soubory
        filtr={}
        filtr['db'] = gtk.FileFilter()
        filtr['db'].add_pattern('*.db')
        filtr['vse'] = gtk.FileFilter()
        filtr['vse'].add_pattern('*')

        # změna filtru pro zobrazované soubory
        def cbOtevriDBTypSouboru_changed(widget, data=None):
            if cbOtevriDBTypSouboru.get_active() == 0:
                self.wOtevritDB.set_filter(filtr['db'])
            else:
                self.wOtevritDB.set_filter(filtr['vse'])
                
        
        # xml strom pro otevírací dialog
        xmlOtevritDB = gtk.glade.XML(BenedatGladeFile.gladefile, "wOtevritDB")
        self.wOtevritDB = xmlOtevritDB.get_widget("wOtevritDB")
        # box pro výběr typu souboru
        cbOtevriDBTypSouboru = xmlOtevritDB.get_widget("cbOtevriDBTypSouboru")
        # vyplnění boxu pro výběr souboru
        self.model_scrit = gtk.ListStore(str)
        self.model_scrit.append(["Pouze databázové soubory (*.db)"])
        self.model_scrit.append(["Všechny soubory"])
        cbOtevriDBTypSouboru.set_model(self.model_scrit)
        cell = gtk.CellRendererText()
        cbOtevriDBTypSouboru.pack_start(cell)
        cbOtevriDBTypSouboru.add_attribute(cell,'text',0)
        cbOtevriDBTypSouboru.set_active(0)
        # připojení signálu pro změnu
        cbOtevriDBTypSouboru.connect('changed', cbOtevriDBTypSouboru_changed)
        #nastavení výchozího filtru na db
        self.wOtevritDB.set_filter(filtr['db'])   

        navratova_hodnota = self.wOtevritDB.run()
        
        # kontrola vybraného souboru
        if navratova_hodnota == gtk.RESPONSE_OK and self.wOtevritDB.get_filename():
            self.databazovy_soubor = self.wOtevritDB.get_filename().decode("utf-8")
            self.wOtevritDB.destroy()
            self.otevreni_db()
        else:
            self.wOtevritDB.destroy()
    

    def otevreni_db(self):
        """kontrola a otevření databáze"""
        try:
            if not os.path.isfile(self.databazovy_soubor):
                raise berr.ChybaDB("Vybraný soubor %s neexistuje!" % self.databazovy_soubor)
#            print "Byl vybrán soubor: %s" % self.databazovy_soubor
            # vytvoření zálohy souboru
            self.zalozni_db_soubor = os.path.join(
                        os.path.dirname(self.databazovy_soubor),
                        "." + 
                        os.path.basename(self.databazovy_soubor) +
                        "~")
            shutil.copyfile(self.databazovy_soubor,
                    self.zalozni_db_soubor)


            BenedatDB.db = bsqlite.Db(self.databazovy_soubor)
            self.konf.volba("otevreny_soubor", self.databazovy_soubor)
            BenedatDB.db_soubor = self.databazovy_soubor
            self.povol_tlacitka_zavisla_na_db()
            self.nastav_statusbar("..." + self.databazovy_soubor[-30:])
        except berr.ChybaDB, e: 
            # vybraný soubor není souborem databáze nebo je nekorektní
            dialogChyba(e)
            self.databazovy_soubor = None
            BenedatDB.db_soubor = self.databazovy_soubor
            self.konf.volba("otevreny_soubor", self.databazovy_soubor)
            self.zakaz_tlacitka_zavisla_na_db()
            self.nastav_statusbar("..." + self.databazovy_soubor[-30:])
        except berr.ChybaJinaVerzeDB, e:
            # dotaz na povýšení verze
            navratova_hodnota = dialogDotaz(
                    text="Databáze je v jiné verzi než vyžaduje tato verze programu!",
                    text_dalsi="Aktualizovat databázi na novější verzi?")
            if gtk.RESPONSE_YES== navratova_hodnota:
                # aktualizace databáze na novější verzi
                # vytvoření zálohy souboru
                self.zalozni_db_soubor = os.path.join(
                        os.path.dirname(self.databazovy_soubor),
                        ".STARSI_VERZE_" + 
                        os.path.basename(self.databazovy_soubor) +
                        "~")
                shutil.copyfile(self.databazovy_soubor,
                        self.zalozni_db_soubor)
                # aktualizace db 
                bsqlite.aktualizace_db_na_novejsi_verzi(self.databazovy_soubor)
                # a otevření databáze
                self.otevreni_db()

            else:
#                dialogChyba(e)
                self.databazovy_soubor = None
                BenedatDB.db_soubor = self.databazovy_soubor
                self.konf.volba("otevreny_soubor", self.databazovy_soubor)
                self.zakaz_tlacitka_zavisla_na_db()
                self.nastav_statusbar(self.databazovy_soubor)


            

    def nastav_statusbar(self,text):
        self.wHlavniWidgety['sbHlavni'].push(0, str(text))


       
    def on_btEditaceZaznamuOS_clicked(self, widget):
        oknoZaznamyOS = BenedatOknoZaznamyOS()
        oknoZaznamyOS.run()

    def dialog_sestavy(self, widget):
        oknoSestavyOS = BenedatOknoSestavy()
        oknoSestavyOS.run()


    def klienti(self,widget):
        oknoKlienti = BenedatOknoKlienti()
        oknoKlienti.run()


    # funkce pro nastavení citlivosti tlačítek - v případě otevřené nebo neotevřené databáze
    def povol_tlacitka_zavisla_na_db(self):
        self.wHlavniWidgety['btUlozDb'].set_property("sensitive", True)
        self.wHlavniWidgety['btZavriDb'].set_property("sensitive", True)
        self.wHlavniWidgety['btEditaceZaznamuOS'].set_property("sensitive", True)
        self.wHlavniWidgety['btSestavyOS'].set_property("sensitive", True)
        self.wHlavniWidgety['btKlienti'].set_property("sensitive", True)
        self.wHlavniWidgety['btExport'].set_property("sensitive", True)
        self.wHlavniWidgety['btNastaveni'].set_property("sensitive", True)
        self.wHlavniWidgety['btPrazdnaKopie'].set_property("sensitive", True)
#        self.wHlavniWidgety[''].set_property("sensitive", True)

    def zakaz_tlacitka_zavisla_na_db(self):
        self.wHlavniWidgety['btUlozDb'].set_property("sensitive", False)
        self.wHlavniWidgety['btZavriDb'].set_property("sensitive", False)
        self.wHlavniWidgety['btEditaceZaznamuOS'].set_property("sensitive", False)
        self.wHlavniWidgety['btSestavyOS'].set_property("sensitive", False)
        self.wHlavniWidgety['btKlienti'].set_property("sensitive", False)
        self.wHlavniWidgety['btExport'].set_property("sensitive", False)
        self.wHlavniWidgety['btNastaveni'].set_property("sensitive", False)
        self.wHlavniWidgety['btPrazdnaKopie'].set_property("sensitive", False)
#        self.wHlavniWidgety[''].set_property("sensitive", False)

    def dialog_nastaveni(self, widget):
        oknoNastaveni = BenedatOknoNastaveni()
        oknoNastaveni.run()

    def on_btPrazdnaKopie_clicked(self, widget):
        """Vytvoření kopie stávající db bez záznamů (os)"""
        soubor = self.dialog_prazdna_kopie_db()
        if soubor:
            self.prazdna_kopie_db(soubor)

    def prazdna_kopie_db(self, soubor):
        """Vytvoření kopie stávající db bez záznamů (os)"""
        shutil.copyfile(self.databazovy_soubor,
                soubor)
        bsqlite.vyprazdneni_zaznamu_z_db(soubor)

        
    def dialog_prazdna_kopie_db(self):
        # filtry pro zobrazované soubory
        filtr={}
        filtr['db'] = gtk.FileFilter()
        filtr['db'].add_pattern('*.db')
        filtr['vse'] = gtk.FileFilter()
        filtr['vse'].add_pattern('*')

        # změna filtru pro zobrazované soubory
        def cbKopieDBTypSouboru_changed(widget, data=None):
            if cbKopieDBTypSouboru.get_active() == 0:
                self.wKopieDB.set_filter(filtr['db'])
            else:
                self.wKopieDB.set_filter(filtr['vse'])

        # xml strom pro dialog
        xmlKopieDB = gtk.glade.XML(BenedatGladeFile.gladefile, "wKopieDB")
        self.wKopieDB = xmlKopieDB.get_widget("wKopieDB")
#        self.wKopieDB.connect('confirm-overwrite', on_wKopieDB_confirm_overwrite)
        # box pro výběr typu souboru
        cbKopieDBTypSouboru = xmlKopieDB.get_widget("cbKopieDBTypSouboru")
        # vyplnění boxu pro výběr souboru
        self.model_scrit = gtk.ListStore(str)
        self.model_scrit.append(["Pouze databázové soubory (*.db)"])
        self.model_scrit.append(["Všechny soubory"])
        cbKopieDBTypSouboru.set_model(self.model_scrit)
        cell = gtk.CellRendererText()
        cbKopieDBTypSouboru.pack_start(cell)
        cbKopieDBTypSouboru.add_attribute(cell,'text',0)
        cbKopieDBTypSouboru.set_active(0)
        # připojení signálu pro změnu
        cbKopieDBTypSouboru.connect('changed', cbKopieDBTypSouboru_changed)
        #nastavení výchozího filtru na db
        self.wKopieDB.set_filter(filtr['db'])
        
#        self.wKopieDB.set_do_overwrite_confirmation(True)

        navratova_hodnota = self.wKopieDB.run()
        
        # kontrola vybraného souboru
        if navratova_hodnota == gtk.RESPONSE_OK and self.wKopieDB.get_filename():
            soubor = self.wKopieDB.get_filename().decode("utf-8")
            if os.path.splitext(soubor)[1] != ".db":
                soubor += ".db"
            self.wKopieDB.destroy()
            return soubor
        else:
            self.wKopieDB.destroy()
            return None




class BenedatOknoKlienti(BenedatGladeFile, BenedatDB):
    """Okno pro zobrazení a editaci klientů"""
    def __init__(self):
        
        self.wKlientiXml = gtk.glade.XML(BenedatGladeFile.gladefile, "wKlienti")
        self.wKlienti = self.wKlientiXml.get_widget("wKlienti")

        signaly = { 'on_wKlienti_destroy': self.nic,
                    'on_btKlientNovy_clicked': self.on_btKlientNovy_clicked,
                    'on_btKlientSmazat_clicked': self.on_btKlientSmazat_clicked,
                    'on_btKlientUlozit_clicked': self.on_btKlientUlozit_clicked,
                    'on_btKlientZavrit_clicked': self.btKlient_zavrit,
                    'on_twTabKlientu_row_activated': self.on_twTabKlientu_row_activated,
                    'on_chKlienti_OS_toggled': self.on_chKlienti_OS_toggled}
        self.wKlientiXml.signal_autoconnect(signaly)

        self.aktualni_klient = []
        self.editacni_pole = ['Jmeno',
                'Prijmeni',
                'Adresa',
                'Telefon',
                'Mobil1',
                'Mobil2',
                'Pozn',
                'Vzdalenost',
                'NastaveniOS_pausal',
                'NastaveniOS_pausalHodin',
                'NastaveniOS_cena_do',
                'NastaveniOS_cena_mezi',
                'NastaveniOS_cena_nad',
                'typ_dokladu']
        self.edWidgety = {}
        for pole in self.editacni_pole:
            self.edWidgety[pole] = self.wKlientiXml.get_widget("eKlienti_" + pole)
                
        self.chWidgety = {}
        self.check_boxy = ['OS', 'OA']
        for box in self.check_boxy:
            self.chWidgety[box] = self.wKlientiXml.get_widget("chKlienti_" + box)

        self.expWidgety = {}
        self.expandery = ['OS']
        for expander in self.expandery:
            self.expWidgety[expander] = self.wKlientiXml.get_widget("expKlienti_" + expander)

        self.combo_boxy = ['TypDokladu']
        self.cbWidgety = {}
        for widget in self.combo_boxy:
            self.cbWidgety[widget] = self.wKlientiXml.get_widget("cbKlienti_" + widget)


        # vložení typů dokladů do combo boxu
        self.vytvor_cb_typy_dokladu()
        
        # načtení widgetu pro tabulku klientů
        self.tabKlientu = self.wKlientiXml.get_widget("twTabKlientu")
        
        self.sloupce_poradi = [ 'id', 'prijmeni', 'jmeno', 'adresa', 
                                'telefon', 'mobil1', 'mobil2', 'pozn',
                                'os', 'oa', 'km_os']

        
        self.vytvoreni_list_store_klientu()
        self.vytvoreni_sloupcu_v_tab_klientu()
#        self.vytvoreni_bunek_pro_klienty()

#        self.tabKlientu.set_search_column(1)
        self.sloupce['id'].set_sort_column_id(0)
        self.sloupce['prijmeni'].set_sort_column_id(2)
#        self.sloupce['jmeno'].set_sort_column_id(0)
#        self.tabKlientu.set_reorderable(True)
        
        self.tabKlientu.set_enable_search(True)
        self.tabKlientu.set_search_column(2)

        self.nacteni_klientu_z_db()

        # připojení signálu pro jednoduchý výběr klienta
        self.tabKlientu.get_selection().connect('changed',lambda s: self.activate_selected(s))

        
        # callback pro výběr klienta pouhým kliknutím na něj (a jeho vyplnění do formuláře pro editaci
    def activate_selected(self, tabKlientuSelection):
        (model,iter)=tabKlientuSelection.get_selected()
        if iter:
            id_klienta = self.klientiList.get_value(iter, 0)
            self.vyplnit_klienta_do_form(id_klienta)
        else :
            self.vyprazdnit_form()


    def vytvor_cb_typy_dokladu(self):
        """doplnění typů dokladů do comboboxu"""
        cb = self.cbWidgety['TypDokladu']
        typ_dokladuList = gtk.ListStore(int, str)
        cb.set_model(typ_dokladuList)
        cell = gtk.CellRendererText()
        cb.pack_start(cell, True)
        cb.add_attribute(cell, 'text', 1)

        typ_dokladuList.clear()
        typy_dokladu = {0 : 'Příjmový pokladní doklad',
                        1 : 'Jednoduchý výpis'}
        typy_dokladu_poradi = [0, 1]
        for typ_dokladu in typy_dokladu_poradi:
            iter = typ_dokladuList.append()
            typ_dokladuList.set(iter,
                    0, typ_dokladu,
                    1, typy_dokladu[typ_dokladu])
        cb.set_active(0)

    def vytvoreni_sloupcu_v_tab_klientu(self):
        self.sloupce = {}
        self.sloupce['id'] = gtk.TreeViewColumn("ID",
                gtk.CellRendererText(),
                text=0)
        self.sloupce['jmeno'] = gtk.TreeViewColumn("Jméno",
                gtk.CellRendererText(),
                text=1)
        self.sloupce['prijmeni'] = gtk.TreeViewColumn("Příjmení",
                gtk.CellRendererText(),
                text=2)
        self.sloupce['adresa'] = gtk.TreeViewColumn("Adresa",
                gtk.CellRendererText(),
                text=3)
        self.sloupce['telefon'] = gtk.TreeViewColumn("Telefon",
                gtk.CellRendererText(),
                text=4)
        self.sloupce['mobil1'] = gtk.TreeViewColumn("Mobil 1",
                gtk.CellRendererText(),
                text=5)
        self.sloupce['mobil2'] = gtk.TreeViewColumn("Mobil 2",
                gtk.CellRendererText(),
                text=6)
        self.sloupce['pozn'] = gtk.TreeViewColumn("Poznámka",
                gtk.CellRendererText(),
                text=7)
        self.sloupce['os'] = gtk.TreeViewColumn("OS",
                gtk.CellRendererToggle(),
                active=8)
        self.sloupce['oa'] = gtk.TreeViewColumn("OA",
                gtk.CellRendererToggle(),
                active=9)
        self.sloupce['km_os'] = gtk.TreeViewColumn("Vzdálenost",
                gtk.CellRendererText(),
                text=10)
        for sloupec in self.sloupce_poradi:
            self.tabKlientu.append_column(self.sloupce[sloupec])
        # nastavení možnosti zvětšování
#        self.sloupce['id']
#        self.sloupce['jmeno']
#        self.sloupce['prijmeni']
#        self.sloupce['adresa']
#        self.sloupce['telefon']
#        self.sloupce['mobil1']
#        self.sloupce['mobil2']
#        self.sloupce['pozn']
#        self.sloupce['os']
#        self.sloupce['oa']
#        self.sloupce['km_os']


    def vytvoreni_list_store_klientu(self):
        self.klientiList = gtk.ListStore(int, str, str, str, 
                                        str, str, str, str, 
                                        gobject.TYPE_BOOLEAN,
                                        gobject.TYPE_BOOLEAN, str)
        self.tabKlientu.set_model(self.klientiList)	

#    def vytvoreni_bunek_pro_klienty(self):
#        self.bunky = {}
#        self.bunky['id'] = gtk.CellRendererText()
#        self.bunky['jmeno'] = gtk.CellRendererText()
#        self.bunky['prijmeni'] = gtk.CellRendererText()
#        self.bunky['adresa'] = gtk.CellRendererText()
#        self.bunky['telefon'] = gtk.CellRendererText()
#        self.bunky['mobil1'] = gtk.CellRendererText()
#        self.bunky['mobil2'] = gtk.CellRendererText()
#        self.bunky['pozn'] = gtk.CellRendererText()
#        self.bunky['os'] = gtk.CellRendererText()
#        self.bunky['oa'] = gtk.CellRendererText()
#        self.bunky['km_os'] = gtk.CellRendererText()
#        for sloupec in self.sloupce_poradi:
#            self.sloupce[sloupec].pack_start(self.bunky[sloupec], True)
#            self.sloupce[sloupec].set_attributes(self.bunky[sloupec],visible=1)
#            self.sloupce[sloupec].set_property("visible", True)
#            self.sloupce[sloupec].set_property("text", i)
#            i += 1


    
    def nacteni_klientu_z_db(self):
        """Funkce pro načtení klientů z databáze a vyplnění tabulky."""
        klienti = BenedatDB.db.klienti()
#        for id_klienta,jmeno,prijmeni,adresa,telefon,mobil1,mobil2,pozn,os,oa,km_os in klienti:
#            print [id_klienta, prijmeni, jmeno, adresa, telefon, mobil1, mobil2, pozn, os, oa, km_os]
#            self.klientiList.append([id_klienta,
#                                    prijmeni,
#                                    jmeno,
#                                    adresa,
#                                    telefon,
#                                    mobil1,
#                                    mobil2,
#                                    pozn,
#                                    os,
#                                    oa,
#                                    km_os])
        self.klientiList.clear()
        for klient in klienti:
            iter = self.klientiList.append()
            self.klientiList.set(iter,
                     0, klient[ 0],
                     1, klient[ 1],
                     2, klient[ 2],
                     3, klient[ 3],
                     4, klient[ 4],
                     5, klient[ 5],
                     6, klient[ 6],
                     7, klient[ 7],
                     8, bool(klient[ 8]),
                     9, bool(klient[ 9]),
                    10, klient[10])

        

    def vyplnit_klienta_do_form(self, id_klienta = None):
        """vyplnění údajů o klientovy do editačních polí"""
        if id_klienta:
            klient = BenedatDB.db.klient_podle_id(id_klienta)
            self.aktualni_klient = klient
        #print klient
        if klient:
            self.edWidgety['Jmeno'].set_text(bez_none(self.aktualni_klient[1]))
            self.edWidgety['Prijmeni'].set_text(bez_none(self.aktualni_klient[2]))
            self.edWidgety['Adresa'].set_text(bez_none(self.aktualni_klient[3]))
            self.edWidgety['Telefon'].set_text(bez_none(self.aktualni_klient[4]))
            self.edWidgety['Mobil1'].set_text(bez_none(self.aktualni_klient[5]))
            self.edWidgety['Mobil2'].set_text(bez_none(self.aktualni_klient[6]))
            self.edWidgety['Pozn'].set_text(bez_none(self.aktualni_klient[7]))
            self.edWidgety['Vzdalenost'].set_text(bez_none(self.aktualni_klient[10]))

            self.chWidgety['OS'].set_active(bool(self.aktualni_klient[8]))
            self.chWidgety['OA'].set_active(bool(self.aktualni_klient[9]))

            self.edWidgety['NastaveniOS_pausal'].set_text(bez_none(self.aktualni_klient[11]))
            self.edWidgety['NastaveniOS_cena_do'].set_text(bez_none(self.aktualni_klient[12]))
            self.edWidgety['NastaveniOS_cena_mezi'].set_text(bez_none(self.aktualni_klient[13]))
            self.edWidgety['NastaveniOS_cena_nad'].set_text(bez_none(self.aktualni_klient[14]))
            self.edWidgety['NastaveniOS_pausalHodin'].set_text(bez_none(self.aktualni_klient[15]))

            self.cbWidgety['TypDokladu'].set_active(self.aktualni_klient[16])
        else:
            self.vyprazdnit_form()

    def vyprazdnit_form(self):
        """Vyprázdnění všech polí formuláře"""
        self.edWidgety['Jmeno'].set_text("")
        self.edWidgety['Prijmeni'].set_text("")
        self.edWidgety['Adresa'].set_text("")
        self.edWidgety['Telefon'].set_text("")
        self.edWidgety['Mobil1'].set_text("")
        self.edWidgety['Mobil2'].set_text("")
        self.edWidgety['Pozn'].set_text("")
        self.edWidgety['Vzdalenost'].set_text("")

        self.chWidgety['OS'].set_active(False)
        self.chWidgety['OA'].set_active(False)

        self.edWidgety['NastaveniOS_pausal'].set_text("")
        self.edWidgety['NastaveniOS_cena_do'].set_text("")
        self.edWidgety['NastaveniOS_cena_mezi'].set_text("")
        self.edWidgety['NastaveniOS_cena_nad'].set_text("")
        self.edWidgety['NastaveniOS_pausalHodin'].set_text("")

        self.cbWidgety['TypDokladu'].set_active(0)

    def nacteni_klienta_z_form(self):
        """načtení klienta z form do self.aktualni_klient"""
        tmp_vzdalenost = self.edWidgety['Vzdalenost'].get_text()
        if not tmp_vzdalenost:
            tmp_vzdalenost = "0"
        tmp_NastaveniOS_pausal = self.edWidgety['NastaveniOS_pausal'].get_text()
        if not tmp_NastaveniOS_pausal:
            tmp_NastaveniOS_pausal = 0
        tmp_NastaveniOS_cena_do = self.edWidgety['NastaveniOS_cena_do'].get_text()
        if not tmp_NastaveniOS_cena_do:
            tmp_NastaveniOS_cena_do = 0
        tmp_NastaveniOS_cena_mezi = self.edWidgety['NastaveniOS_cena_mezi'].get_text()
        if not tmp_NastaveniOS_cena_mezi:
            tmp_NastaveniOS_cena_mezi = 0
        tmp_NastaveniOS_cena_nad = self.edWidgety['NastaveniOS_cena_nad'].get_text()
        if not tmp_NastaveniOS_cena_nad: 
            tmp_NastaveniOS_cena_nad = 0
        tmp_NastaveniOS_pausalHodin = self.edWidgety['NastaveniOS_pausalHodin'].get_text()
        if not tmp_NastaveniOS_pausalHodin:
            tmp_NastaveniOS_pausalHodin = 0
        tmp_TypDokladu= self.cbWidgety['TypDokladu'].get_active()
        if not tmp_TypDokladu:
            tmp_TypDokladu = 0
        klient = [self.aktualni_klient[0],
                self.edWidgety['Jmeno'].get_text(),
                self.edWidgety['Prijmeni'].get_text(),
                self.edWidgety['Adresa'].get_text(),
                self.edWidgety['Telefon'].get_text(),
                self.edWidgety['Mobil1'].get_text(),
                self.edWidgety['Mobil2'].get_text(),
                self.edWidgety['Pozn'].get_text(),
                int(self.chWidgety['OS'].get_active()),
                int(self.chWidgety['OA'].get_active()),
                tmp_vzdalenost,
                tmp_NastaveniOS_pausal,
                tmp_NastaveniOS_cena_do,
                tmp_NastaveniOS_cena_mezi,
                tmp_NastaveniOS_cena_nad,
                tmp_NastaveniOS_pausalHodin, 
                tmp_TypDokladu] 
        self.aktualni_klient = klient

    def nacteni_noveho_klienta_z_form(self):
        """načtení nového klienta z form do self.aktualni_klient"""
        tmp_vzdalenost = self.edWidgety['Vzdalenost'].get_text()
        if not tmp_vzdalenost:
            tmp_vzdalenost = "0"
        tmp_NastaveniOS_pausal = self.edWidgety['NastaveniOS_pausal'].get_text()
        if not tmp_NastaveniOS_pausal:
            tmp_NastaveniOS_pausal = 0
        tmp_NastaveniOS_cena_do = self.edWidgety['NastaveniOS_cena_do'].get_text()
        if not tmp_NastaveniOS_cena_do:
            tmp_NastaveniOS_cena_do = 0
        tmp_NastaveniOS_cena_mezi = self.edWidgety['NastaveniOS_cena_mezi'].get_text()
        if not tmp_NastaveniOS_cena_mezi:
            tmp_NastaveniOS_cena_mezi = 0
        tmp_NastaveniOS_cena_nad = self.edWidgety['NastaveniOS_cena_nad'].get_text()
        if not tmp_NastaveniOS_cena_nad: 
            tmp_NastaveniOS_cena_nad = 0
        tmp_NastaveniOS_pausalHodin = self.edWidgety['NastaveniOS_pausalHodin'].get_text()
        if not tmp_NastaveniOS_pausalHodin:
            tmp_NastaveniOS_pausalHodin = 0
        tmp_TypDokladu= self.cbWidgety['TypDokladu'].get_active()
        if not tmp_TypDokladu:
            tmp_TypDokladu = 0
        klient = [0,
                self.edWidgety['Jmeno'].get_text(),
                self.edWidgety['Prijmeni'].get_text(),
                self.edWidgety['Adresa'].get_text(),
                self.edWidgety['Telefon'].get_text(),
                self.edWidgety['Mobil1'].get_text(),
                self.edWidgety['Mobil2'].get_text(),
                self.edWidgety['Pozn'].get_text(),
                int(self.chWidgety['OS'].get_active()),
                int(self.chWidgety['OA'].get_active()),
                tmp_vzdalenost,
                tmp_NastaveniOS_pausal,
                tmp_NastaveniOS_cena_do,
                tmp_NastaveniOS_cena_mezi,
                tmp_NastaveniOS_cena_nad,
                tmp_NastaveniOS_pausalHodin,
                tmp_TypDokladu] 
        self.aktualni_klient = klient



    def ulozit_klienta_do_db(self):
        """Uložení změn existujícího klienta"""
        k = self.aktualni_klient
        
        BenedatDB.db.zmen_klienta(k[0],
                                k[ 1],
                                k[ 2],
                                k[ 3],
                                k[ 4],
                                k[ 5],
                                k[ 6],
                                k[ 7],
                                k[ 8],
                                k[ 9],
                                k[10],
                                k[11],
                                k[12],
                                k[13],
                                k[14],
                                k[15],
                                k[16])
        BenedatDB.ulozeno = False

            

    def ulozit_noveho_klienta_do_db(self):
        """vložení nového klienta do db"""
        k = self.aktualni_klient

        BenedatDB.db.vloz_klienta(k[ 1],
                                k[ 2],
                                k[ 3],
                                k[ 4],
                                k[ 5],
                                k[ 6],
                                k[ 7],
                                k[ 8],
                                k[ 9],
                                k[10],
                                k[11],
                                k[12],
                                k[13],
                                k[14],
                                k[15],
                                k[16])
        BenedatDB.ulozeno = False

        

    def run(self):
        self.wKlienti.show_all()


    def nic(self, widget, parametry=None):
        if parametry:
            print parametry

    def destroy(self):
        self.wKlienti.destroy()

    def btKlient_zavrit(self, widget):
        self.destroy()

    def on_twTabKlientu_row_activated(self, widget, path, view_column):
        iter = self.klientiList.get_iter(path)
        id_klienta = self.klientiList.get_value(iter, 0)
        self.vyplnit_klienta_do_form(id_klienta)
        
    def on_chKlienti_OS_toggled(self, widget):
        """rozbalení či sbalení dalšího nastavení pro odlehčovací službu"""
        if self.chWidgety['OS'].get_active():
            self.expWidgety['OS'].set_sensitive(True)
            self.expWidgety['OS'].set_expanded(True)
        else:
            self.expWidgety['OS'].set_sensitive(False)
            self.expWidgety['OS'].set_expanded(False)

    def on_btKlientNovy_clicked(self, widget):
        self.aktualni_klient = []
        self.vyprazdnit_form()
        self.tabKlientu.get_selection().unselect_all()
        self.edWidgety['Jmeno'].grab_focus()


    def on_btKlientUlozit_clicked(self, widget):
        # uložit změny existujícího klienta nebo nového klienta?
        try: 
            if self.aktualni_klient:
                # pouze uložit změny existujícího klienta
                self.nacteni_klienta_z_form()
                self.ulozit_klienta_do_db()
                self.nacteni_klientu_z_db()
                self.vyprazdnit_form()
                self.aktualni_klient = []
            else:
                self.nacteni_noveho_klienta_z_form()
                self.ulozit_noveho_klienta_do_db()
                self.nacteni_klientu_z_db()
                self.vyprazdnit_form()
                self.aktualni_klient = []
            self.uloz_db()
        except berr.ChybaPrazdnePole, e:
            self.aktualni_klient = []
    
    def on_btKlientSmazat_clicked(self, widget):
        if not self.aktualni_klient:
            return
        id_klienta = self.aktualni_klient[0]
        navratova_hodnota = dialogDotaz(text="Opravdu si přejete smazat klienta:",
                text_dalsi=BenedatDB.db.klient_jmeno_podle_id(id_klienta))
        if gtk.RESPONSE_YES == navratova_hodnota:
            BenedatDB.db.smaz_klienta(id_klienta)
            self.nacteni_klientu_z_db()
            self.vyprazdnit_form()
            self.aktualni_klient = []
            BenedatDB.ulozeno = False
            self.uloz_db()


class BenedatOknoZaznamyOS(BenedatGladeFile,BenedatDB):
    """Okno se záznamy odlehčovací služby"""

    def __init__(self):
        self.wZaznamyOSXml = gtk.glade.XML(BenedatGladeFile.gladefile, "wZaznamyOS")
        self.wZaznamyOS = self.wZaznamyOSXml.get_widget("wZaznamyOS")

        signaly = { 'on_wZaznamyOS_destroy': self.on_wZaznamyOS_destroy,
                    'on_btZaznamyOSNovy_clicked': self.on_btZaznamyOSNovy_clicked,
                    'on_btZaznamyOSSmazat_clicked': self.on_btZaznamyOSSmazat_clicked,
                    'on_btZaznamyOSUlozit_clicked': self.on_btZaznamyOSUlozit_clicked,
                    'on_btZaznamyOSZavrit_clicked': self.on_btZaznamyOSZavrit_clicked,
                    'on_cbZaznamyOs_Mesic_changed': self.on_cbZaznamyOs_Mesic_changed,
                    'on_cbZaznamyOs_Rok_changed': self.on_cbZaznamyOs_Rok_changed,
                    'on_chZaznamyOS_Filtr_toggled': self.on_chZaznamyOS_Filtr_toggled,
                    'on_twTabZaznamyOS_row_activated':self.on_twTabZaznamyOS_row_activated,
#                    'on_cbZaznamyOS_Klient_changed': self.on_cbZaznamyOS_Klient_changed,
                    'on_eZaznamyOS_Klient_changed': self.on_eZaznamyOS_Klient_changed,
                    'on_eZaznamyOS_Klient_focus_out_event':self.on_eZaznamyOS_Klient_focus_out_event,
                    'on_eZaznamyOS_Datum_focus_out_event': self.on_eZaznamyOS_Datum_focus_out_event,
                    'on_eZaznamyOS_CasOd_focus_out_event': self.on_eZaznamyOS_CasOd_focus_out_event,
                    'on_eZaznamyOS_CasDo_focus_out_event': self.on_eZaznamyOS_CasDo_focus_out_event,
                    'on_btZaznamyOS_Klient_clicked': self.on_btZaznamyOS_Klient_clicked,
                    'on_btZaznamyOS_Datum_clicked': self.on_btZaznamyOS_Datum_clicked}
        self.wZaznamyOSXml.signal_autoconnect(signaly)

        self.aktualni_zaznam = []

        self.editacni_pole = ['Klient',
                'Datum',
                'CasOd',
                'CasDo',
                'Dovoz',
                'Odvoz',
                'Obcerstveni',
                'Obed',
                'Prenocovani']
        self.edWidgety = {}
        for pole in self.editacni_pole:
            self.edWidgety[pole] = self.wZaznamyOSXml.get_widget("eZaznamyOS_" + pole)

        self.combo_boxy = ['Mesic',
                'Rok' ]#, 'Klient']
        self.cbWidgety = {}
        for widget in self.combo_boxy:
            self.cbWidgety[widget] = self.wZaznamyOSXml.get_widget("cbZaznamyOS_" + widget)

        

    
        
        # Nastavení roku a měsíce na aktuální
        self.mesic = time.strftime('%m')
        self.rok = time.strftime('%Y')
        self.posledni={}
        self.posledni['rok'] = self.rok
        self.posledni['mesic'] = self.mesic
        self.posledni['den'] = time.strftime('%d')
        self.posledni['cas_od'] = '00:00'
        self.posledni['cas_do'] = '00:00'
        self.posledni['klient'] = ""


        self.pouzit_filtr = True
        self.chZaznamyOS_Filtr = self.wZaznamyOSXml.get_widget("chZaznamyOS_Filtr")
        

        self.sloupce_poradi = ['klient', 'datum', 
                                'cas_od', 'cas_do', 
                                'dovoz', 'odvoz',
                                'cena_obcerstveni', 'obed',
                                'prenocovani', 'mezera']


        self.tabZaznamuOS = self.wZaznamyOSXml.get_widget("twTabZaznamyOS")

        self.vytvoreni_list_store_zaznamu_os()
        self.vytvoreni_sloupcu_v_tab_zaznamu_os()

        self.sloupce['klient'].set_sort_column_id(1)
        self.sloupce['datum'].set_sort_column_id(10)

        self.nacteni_zaznamu_os_z_db()

        # připojení signálu pro jednoduchý výběr záznamu
        self.tabZaznamuOS.get_selection().connect('changed',lambda s: self.activate_selected(s))

        
        self.vytvor_cb_mesice()
        self.vytvor_cb_roky()
        self.chZaznamyOS_Filtr.set_active(True)
        
#        self.vyplnit_klienty_do_combo_boxu()
        self.vytvor_klientiList()
        
        self.vytvor_menu_klientu()
        self.doplnovani_ed_klient()


        # callback pro výběr záznamu pouhým kliknutím na něj (a jeho vyplnění do formuláře pro editaci
    def activate_selected(self, tabZaznamuOSSelection):
        (model,iter)=tabZaznamuOSSelection.get_selected()
        if iter:
            id_zaznamu = self.zaznamyOsList.get_value(iter, 0)
            self.vyplnit_zaznam_do_form(id_zaznamu)
        
        



    def vytvoreni_list_store_zaznamu_os(self):
        # id zaznamu, klient, datum, cas_od, cas_do, dovoz, odvoz, cena_obcerstveni, obed, prenocovani, datum_razeni
        self.zaznamyOsList = gtk.ListStore(int, str, str, str, str,
                                            gobject.TYPE_BOOLEAN,
                                            gobject.TYPE_BOOLEAN,
                                            str,
                                            gobject.TYPE_BOOLEAN,
                                            gobject.TYPE_BOOLEAN,
                                            str)
        self.tabZaznamuOS.set_model(self.zaznamyOsList)

    def vytvoreni_sloupcu_v_tab_zaznamu_os(self):
        self.sloupce = {}
        tmp_cell = gtk.CellRendererText()
        tmp_cell.set_property("xalign",0)
        self.sloupce['klient'] = gtk.TreeViewColumn("Klient",
                tmp_cell,
                text=1)
#        self.sloupce['klient'].set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        self.sloupce['klient'].set_min_width(100)

        tmp_cell = gtk.CellRendererText()
        tmp_cell.set_property("xalign",1)
        self.sloupce['datum'] = gtk.TreeViewColumn("Datum",
                tmp_cell,
                text=2)
        self.sloupce['datum'].set_min_width(90)
#        self.sloupce['datum'].set_alignment(0)

        tmp_cell.set_property("xalign",1)
        self.sloupce['cas_od'] = gtk.TreeViewColumn("Čas od",
                tmp_cell,
                text=3)
        self.sloupce['cas_od'].set_min_width(60)
        
        tmp_cell.set_property("xalign",1)
        self.sloupce['cas_do'] = gtk.TreeViewColumn("Čas do",
                tmp_cell,
                text=4)
        self.sloupce['cas_do'].set_min_width(60)
        
        self.sloupce['dovoz'] = gtk.TreeViewColumn("Dovoz",
                gtk.CellRendererToggle(),
                active=5)
        
        self.sloupce['odvoz'] = gtk.TreeViewColumn("Odvoz",
                gtk.CellRendererToggle(),
                active=6)

        tmp_cell = gtk.CellRendererText()
        tmp_cell.set_property("xalign",1)
        self.sloupce['cena_obcerstveni'] = gtk.TreeViewColumn("Občerstvení",
                tmp_cell,
                text=7)
        self.sloupce['cena_obcerstveni'].set_min_width(90)

        self.sloupce['obed'] = gtk.TreeViewColumn("Oběd",
                gtk.CellRendererToggle(),
                active=8)

        self.sloupce['prenocovani'] = gtk.TreeViewColumn("Přenocování",
                gtk.CellRendererToggle(),
                active=9)
#        self.sloupce['odvoz'].set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
#        self.sloupce['odvoz'].set_fixed_width(1)
#        self.sloupce['odvoz'].set_max_width(2)
        
        self.sloupce['mezera'] = gtk.TreeViewColumn('',
                gtk.CellRendererText())


        for sloupec in self.sloupce_poradi:
            self.tabZaznamuOS.append_column(self.sloupce[sloupec])


    def nacteni_zaznamu_os_z_db(self):
        """Funkce pro načtení záznamů os z databáze a vyplnění tabulky."""
        if self.pouzit_filtr and self.rok and self.mesic:
            zaznamy = BenedatDB.db.vypis_zaznamy_os(mesic=self.mesic, rok= self.rok)
        else:
            zaznamy = BenedatDB.db.vypis_zaznamy_os()
        self.zaznamyOsList.clear()
        for zaznam in zaznamy:
            klient = BenedatDB.db.klient_jmeno_podle_id(zaznam[1], 1)
            if not klient:
                klient = zaznam[1]
            iter = self.zaznamyOsList.append()
            self.zaznamyOsList.set(iter,
                    0, zaznam[0],
                    1, klient,
                    2, bcas.preved_datum(zaznam[2],0),
                    3, zaznam[3],
                    4, zaznam[4],
                    5, bool(zaznam[5]),
                    6, bool(zaznam[6]),
                    7, "%0.2f kč" % zaznam[8],
                    8, bool(zaznam[9]),
                    9, bool(zaznam[7]),
                    10, zaznam[2])

    def vytvor_cb_mesice(self):
        """doplnění měsíců do comboboxu"""
        cb = self.cbWidgety['Mesic']
        mesiceList = gtk.ListStore(str, str)
        cb.set_model(mesiceList)
        cell = gtk.CellRendererText()
        cb.pack_start(cell, True)
        cb.add_attribute(cell, 'text', 1)

        mesiceList.clear()
        mesice={'01': 'Leden',
                '02': 'Únor',
                '03': 'Březen',
                '04': 'Duben',
                '05': 'Květen',
                '06': 'Červen',
                '07': 'Červenec',
                '08': 'Srpen',
                '09': 'Září',
                '10': 'Říjen',
                '11': 'Listopad',
                '12': 'Prosinec'}
        mesice_poradi = ['01','02','03','04','05','06',
                '07','08','09','10','11','12']
        for mesic in mesice_poradi:
            iter = mesiceList.append()
            mesiceList.set(iter,
                    0, mesic,
                    1, mesice[mesic])

        cb.set_active(int(self.mesic)-1)

    def on_cbZaznamyOs_Mesic_changed(self, widget):
        """Změna nastavení měsíce"""
        cb = self.cbWidgety['Mesic']
        mesice = cb.get_model()
        index = cb.get_active()
        self.mesic = mesice[index][0]
        
        self.nacteni_zaznamu_os_z_db()

    def vytvor_cb_roky(self):
        """doplnění roků do comboboxu"""
        cb = self.cbWidgety['Rok']
        rokyList = gtk.ListStore(str)
        cb.set_model(rokyList)
        cell = gtk.CellRendererText()
        cb.pack_start(cell, True)
        cb.add_attribute(cell, 'text', 0)

        aktualni_rok = self.rok

        rokyList.clear()
        roky_z_db = BenedatDB.db.zaznamy_pouzite_roky()
        roky = []
        for rok in roky_z_db:
            roky.append(rok[0])
        if not aktualni_rok in roky:
            roky.append(aktualni_rok)
        
        for rok in roky:
            iter = rokyList.append()
            rokyList.set(iter,
                    0, rok)

        # Zjištění pozice aktuálního roku a jeho vybrání
        i = 0
        for rok in cb.get_model():
            if rok[0] == aktualni_rok:
                break
            else:
                i+=1

        cb.set_active(i)

    def on_cbZaznamyOs_Rok_changed(self, widget):
        """Změna nastavení roku"""
        cb = self.cbWidgety['Rok']
        roky = cb.get_model()
        index = cb.get_active()
        self.rok = roky[index][0]
        self.nacteni_zaznamu_os_z_db()

            
    def on_chZaznamyOS_Filtr_toggled(self,widget):
        """změna nastavení použití filtru"""
        self.pouzit_filtr = self.chZaznamyOS_Filtr.get_active()
        self.nacteni_zaznamu_os_z_db()

    def vyplnit_zaznam_do_form(self, id_zaznamu=None):
        """Vyplnění záznamu do editačního pole"""
        if id_zaznamu:
            zaznam = BenedatDB.db.vypis_zaznamy_os(zaznam_id=id_zaznamu)
            self.aktualni_zaznam = zaznam

            klient = BenedatDB.db.klient_jmeno_podle_id(zaznam[1], 1)
            if not klient:
                klient = str(zaznam[1])
        if self.aktualni_zaznam:
            self.edWidgety['Klient'].set_text(klient)
            self.edWidgety['Datum'].set_text(bcas.preved_datum(bez_none(self.aktualni_zaznam[2]),0))
            self.edWidgety['CasOd'].set_text(bez_none(self.aktualni_zaznam[3]))
            self.edWidgety['CasDo'].set_text(bez_none(self.aktualni_zaznam[4]))
            self.edWidgety['Dovoz'].set_active(bool(self.aktualni_zaznam[5]))
            self.edWidgety['Odvoz'].set_active(bool(self.aktualni_zaznam[6]))
            self.edWidgety['Prenocovani'].set_active(bool(self.aktualni_zaznam[7]))
            self.edWidgety['Obcerstveni'].set_text(bez_none(self.aktualni_zaznam[8]))
            self.edWidgety['Obed'].set_active(bool(self.aktualni_zaznam[9]))
        else:
            self.vyprazdnit_form()

    def vyprazdnit_form(self):
        """Vyprázdnění formuláře"""
        self.edWidgety['Klient'].set_text("")
        self.edWidgety['Datum'].set_text("")
        self.edWidgety['CasOd'].set_text("")
        self.edWidgety['CasDo'].set_text("")
        self.edWidgety['Dovoz'].set_active(False)
        self.edWidgety['Odvoz'].set_active(False)
        self.edWidgety['Prenocovani'].set_active(False)
        self.edWidgety['Obcerstveni'].set_text("")
        self.edWidgety['Obed'].set_active(False)

    def vytvor_klientiList(self):
        """Vytvoření seznamu klientů"""
        self.klientiList = gtk.ListStore(int, str)
        self.klientiList.clear()
        # klienti_z_db_pj = Příjmení Jméno
        klienti_z_db_pj = BenedatDB.db.klienti_id_jmeno(1,pouze='os')

#       setřídění
        setrideny_seznam_klientu = setrideni_slovniku_podle_obsahu(klienti_z_db_pj)

        for klient in setrideny_seznam_klientu:
            iter = self.klientiList.append()
            self.klientiList.set(iter,
                    0, klient,
                    1, klienti_z_db_pj[klient])

        # umožnit doplňování i v pořadí Jméno Příjmení
        # klienti_z_db_jp = Jméno Příjmení 
        klienti_z_db_jp = (BenedatDB.db.klienti_id_jmeno(0,pouze='os'))
        setrideny_seznam_klientu = setrideni_slovniku_podle_obsahu(klienti_z_db_jp)
        
        for klient in setrideny_seznam_klientu:
            iter = self.klientiList.append()
            self.klientiList.set(iter,
                    0, klient,
                    1, klienti_z_db_jp[klient])
        

#    def vyplnit_klienty_do_combo_boxu(self):
#        """Vyplnění možných klientů do combo boxu"""
#        cb = self.cbWidgety['Klient']
#        self.klientiList = gtk.ListStore(int, str)
#        cb.set_model(self.klientiList)
#        cell = gtk.CellRendererText()
#        cb.pack_start(cell, True)
#        cb.add_attribute(cell, 'text', 1)

#        self.klientiList.clear()
#        klienti_z_db_pj = BenedatDB.db.klienti_id_jmeno(1,pouze='os')

##         setřídění
#        setrideny_seznam_klientu = setrideni_slovniku_podle_obsahu(klienti_z_db_pj)

#        for klient in setrideny_seznam_klientu:
#            iter = self.klientiList.append()
#            self.klientiList.set(iter,
#                    0, klient,
#                    1, klienti_z_db_pj[klient])

#    def on_cbZaznamyOS_Klient_changed(self, widget):
#        """Změna jména v combo boxu"""
#        cb = self.cbWidgety['Klient']
#        klienti = cb.get_model()
#        index = cb.get_active()
#        self.edWidgety['Klient'].set_text(klienti[index][1])

    def doplnovani_ed_klient(self):
        """Vytvoření doplňování pro editační pole klient"""
        completion = gtk.EntryCompletion()
        completion.set_model(self.klientiList)
        self.edWidgety['Klient'].set_completion(completion)
        completion.set_text_column(1)
        completion.set_minimum_key_length(0)


    def urcit_id_klienta_z_textu(self, klient):
        try: 
            id_klienta = int(klient)
        except ValueError:
            id_klienta = BenedatDB.db.klient_id_podle_jmena(klient)

        return id_klienta

    def nacteni_zaznamu_z_form(self):
        """načtení záznamu z formuláře do self.aktualni_zaznam"""
        zaznam = [self.aktualni_zaznam[0],  # 0
                self.urcit_id_klienta_z_textu(self.edWidgety['Klient'].get_text()), # 1
                self.edWidgety['Datum'].get_text(), # 2
                self.edWidgety['CasOd'].get_text(), # 3
                self.edWidgety['CasDo'].get_text(), # 4
                int(self.edWidgety['Dovoz'].get_active()),  # 5
                int(self.edWidgety['Odvoz'].get_active()), # 6
                int(self.edWidgety['Prenocovani'].get_active()),  # 7
                float_or_zero(self.edWidgety['Obcerstveni'].get_text()), # 8
                int(self.edWidgety['Obed'].get_active())] # 9
        self.aktualni_zaznam = zaznam

    def nacteni_noveho_zaznamu_z_form(self):
        """načtení nového záznamu z formuláře do self.aktualni_zaznam"""
        zaznam = [0,
                self.urcit_id_klienta_z_textu(self.edWidgety['Klient'].get_text()), # 1
                self.edWidgety['Datum'].get_text(), # 2
                self.edWidgety['CasOd'].get_text(), # 3
                self.edWidgety['CasDo'].get_text(), # 4
                int(self.edWidgety['Dovoz'].get_active()), # 5
                int(self.edWidgety['Odvoz'].get_active()), # 6
                int(self.edWidgety['Prenocovani'].get_active()), # 7
                float_or_zero(self.edWidgety['Obcerstveni'].get_text()), # 8
                int(self.edWidgety['Obed'].get_active())] # 9
        self.aktualni_zaznam = zaznam

    def overeni_datumu_podle_nastavenych_hodnot(self):
        """Ověření případně dotaz pokud je datum (měsíc a rok) jiný než nastavený ve filtru"""
        if self.pouzit_filtr:
            if int(bcas.mesic(self.aktualni_zaznam[2])) != int(self.mesic) or \
                    int(bcas.rok(self.aktualni_zaznam[2])) != int(self.rok):
                navratova_hodnota = dialogDotaz(
                        text="Zadaný záznam má jiné datum (měsíc a rok) než je nastaveno ve filtru!",
                        text_dalsi="Vložit přesto záznam do databáze?")
                if gtk.RESPONSE_NO == navratova_hodnota:
                    raise berr.ChybaRozdilneDatum()
    
    def kontrola_existence_podobneho_zaznamu(self):
        """Zkontroluje jestli neexistuje podobný záznam (se stejným datem pro konkrétního klienta"""
        z = self.aktualni_zaznam

        if BenedatDB.db.existuje_podobny_zaznam(z[1],bcas.preved_datum(z[2],2)):
            navratova_hodnota = dialogDotaz(
                    text="Zadaný záznam je podobný (klientem a datem) jako záznam již dříve vložený do databáze!",
                    text_dalsi="Vložit přesto záznam do databáze?")
            if gtk.RESPONSE_NO == navratova_hodnota:
                raise berr.ChybaStejnyZaznam()


    def ulozit_zaznam_do_db(self):
        """Uložení změn existujícího klienta"""
        z = self.aktualni_zaznam

        BenedatDB.db.zmen_zaznam_os(z[1],
                                    bcas.preved_datum(z[2],2),
                                    z[3],
                                    z[4],
                                    z[5],
                                    z[6],
                                    z[7],
                                    z[8],
                                    z[9],
                                    z[0])
        BenedatDB.ulozeno = False

    def ulozit_novy_zaznam_do_db(self):
        """Vložení nového záznamu do db"""
        z = self.aktualni_zaznam

        BenedatDB.db.vloz_zaznam_os(z[1],
                                    bcas.preved_datum(z[2],2),
                                    z[3],
                                    z[4],
                                    z[5],
                                    z[6],
                                    z[7],
                                    z[8],
                                    z[9])
        BenedatDB.ulozeno = False

    def vytvor_menu_klientu(self):
        """Vytvoření menu se seznamem klientů"""
        self.MenuKlienti = gtk.Menu()

        klienti_z_db = BenedatDB.db.klienti_id_jmeno(1,pouze='os')
        setrideny_seznam_klientu = setrideni_slovniku_podle_obsahu(klienti_z_db)

        k_item = {}
        for klient in setrideny_seznam_klientu:
            k_item[klient] = gtk.MenuItem(klienti_z_db[klient])
            k_item[klient].connect_object("activate", self.obslouzeni_menu_klientu, klienti_z_db[klient])
            self.MenuKlienti.append(k_item[klient])

        self.MenuKlienti.show_all()

    def obslouzeni_menu_klientu(self, data):
        """Obsloužení kliknutí na položku v menu klientů"""
        self.edWidgety['Klient'].set_text(data)
        self.korekce_klienta(self.edWidgety['Klient'])
        self.edWidgety['Datum'].grab_focus()

    def run(self):
        self.wZaznamyOS.show_all()

    def destroy(self):
        self.wZaznamyOS.destroy()

    def nic(self, widget, parametry=None):
        if parametry:
            print parametry

    def on_wZaznamyOS_destroy(self, widget):
        self.destroy()

    def on_btZaznamyOSZavrit_clicked(self, widget):
        self.destroy()
        self.uloz_db()

    def on_twTabZaznamyOS_row_activated(self, widget, path, view_column):
        """vybrání jednoho záznamu"""
        iter = self.zaznamyOsList.get_iter(path)
        id_zaznamu = self.zaznamyOsList.get_value(iter, 0)
        self.vyplnit_zaznam_do_form(id_zaznamu)

    def on_btZaznamyOSUlozit_clicked(self, widget):
        """Obsloužení tlačítka Uložit"""
        if not self.urcit_id_klienta_z_textu(self.edWidgety['Klient'].get_text()):
            self.edWidgety['Klient'].grab_focus()
            return
        self.korekce_klienta(self.edWidgety['Klient'])
        self.korekce_datumu(self.edWidgety['Datum'])
        self.korekce_casu(self.edWidgety['CasOd'],'cas_od')
        self.korekce_casu(self.edWidgety['CasDo'],'cas_do')
        try:
            if self.aktualni_zaznam:
                # pouze uložit změny existujícího záznamu
                self.nacteni_zaznamu_z_form()
                self.overeni_datumu_podle_nastavenych_hodnot()
                self.ulozit_zaznam_do_db()
                self.nacteni_zaznamu_os_z_db()
                self.vyprazdnit_form()
                self.aktualni_zaznam = []
            else:
                # vložení nového záznamu
                self.nacteni_noveho_zaznamu_z_form()
                self.overeni_datumu_podle_nastavenych_hodnot()
                self.kontrola_existence_podobneho_zaznamu()
                self.ulozit_novy_zaznam_do_db()
                self.nacteni_zaznamu_os_z_db()
                self.vyprazdnit_form()
                self.aktualni_zaznam = []
        except berr.ChybaPrazdnePole, e:
            log(e)
            self.aktualni_klient = []
        except berr.ChybaRozdilneDatum:
            self.aktualni_zaznam = []
            pass
        except berr.ChybaStejnyZaznam:
            self.aktualni_zaznam = []
            pass

#        print self.urcit_id_klienta_z_textu(self.edWidgety['Klient'].get_text())
#        self.vyprazdnit_form()
        self.edWidgety['Klient'].grab_focus()


    def on_btZaznamyOSSmazat_clicked(self, widget):
        """ Obsloužení tlačítka pro smazání záznamu"""
        if not self.aktualni_zaznam:
            return
        id_zaznamu = self.aktualni_zaznam[0]
        az = self.aktualni_zaznam
        navratova_hodnota = dialogDotaz(text="Opravdu si přejete smazat záznam:", 
                text_dalsi = BenedatDB.db.klient_jmeno_podle_id(az[1]) + ": " + \
                    az[2] + " od " + az[3] + \
                    " do " + az[4] + ".")
        if gtk.RESPONSE_YES == navratova_hodnota:
            BenedatDB.db.smaz_zaznam_os(id_zaznamu)
            self.nacteni_zaznamu_os_z_db()
            self.vyprazdnit_form()
            self.aktualni_zaznam = []
            BenedatDB.ulozeno = False

    def on_btZaznamyOSNovy_clicked(self, widget):
        """Obsloužení tlačítka Nový"""
        self.aktualni_zaznam = []
        self.vyprazdnit_form()
        self.tabZaznamuOS.get_selection().unselect_all()
        self.edWidgety['Klient'].grab_focus()

    def on_btZaznamyOS_Klient_clicked(self, widget):
        """Tlačítko pro zobrazení menu klientů"""

#        self.vytvor_menu_klientu()
        self.MenuKlienti.popup(None, None, None, 0, 0)




    def on_eZaznamyOS_Klient_changed(self,widget):
        pass

    def on_eZaznamyOS_Klient_focus_out_event(self, widget, event):
        """Obsloužení opuštění editačního pole"""
        self.korekce_klienta(widget)
#            widget.grab_focus()

    def on_btZaznamyOS_Datum_clicked(self, widget):
        datum = dialogKalendar(self.wZaznamyOS)
        if datum:
            self.edWidgety['Datum'].set_text(datum)
            self.on_eZaznamyOS_Datum_focus_out_event(self.edWidgety['Datum'], None)

    def on_eZaznamyOS_Datum_focus_out_event(self, widget, event):
        """Kontrola případně doplnění datumu"""
        self.korekce_datumu(widget)
        

    def on_eZaznamyOS_CasOd_focus_out_event(self, widget, event):
        """Kontrola případně doplnění počátečního času"""
        self.korekce_casu(widget, 'cas_od')


    def on_eZaznamyOS_CasDo_focus_out_event(self, widget, event):
        """Kontrola případně doplnění koncového času"""
        self.korekce_casu(widget, 'cas_do')

    def korekce_klienta(self, widget):
        """Kontrola případně změna klienta"""
        if not self.urcit_id_klienta_z_textu(widget.get_text()):
            widget.set_text(self.posledni['klient'])
        self.posledni['klient'] = widget.get_text()

    def korekce_datumu(self, widget):
        """Kontrola případně doplnění datumu"""
        zadane_datum = widget.get_text()
        zadane_datum = bcas.preved_datum(zadane_datum, 0, self.posledni)
        if not zadane_datum:
            zadane_datum = self.posledni['den'] + "." + \
                            self.posledni['mesic'] + "." + \
                            self.posledni['rok']
        (self.posledni['den'], self.posledni['mesic'], self.posledni['rok']) = \
            string.split(zadane_datum, '.')
        widget.set_text(zadane_datum)
        
    def korekce_casu(self,widget,oddo):
        zadany_cas = widget.get_text()
        zadany_cas = bcas.preved_cas(zadany_cas, 0)
        if not zadany_cas:
            zadany_cas = self.posledni[oddo]
        self.posledni[oddo] = zadany_cas
        widget.set_text(zadany_cas)



class BenedatOknoSestavy(BenedatGladeFile,BenedatDB):
    """Okno pro generování sestav"""
    
    def __init__(self):
        self.wSestavyOSXml = gtk.glade.XML(BenedatGladeFile.gladefile, "wSestavyOS")
        self.wSestavyOS = self.wSestavyOSXml.get_widget("wSestavyOS")

        signaly = { 'on_wSestavyOS_destroy': self.on_wSestavyOS_destroy,
                'on_btSestavyOS_Zavrit_clicked': self.on_btSestavyOS_Zavrit_clicked,
                'on_btSestavyOS_Ulozit_clicked': self.on_btSestavyOS_Ulozit_clicked,
#                'on_chSestavyOS_vsichni_toggled': self.on_chSestavyOS_vsichni_toggled,
#                'on_cbSestavyOS_Klient_changed': self.on_cbSestavyOS_Klient_changed,
                'on_cbSestavyOS_Mesic_changed': self.on_cbZaznamyOs_Mesic_changed,
                'on_cbSestavyOS_Rok_changed': self.on_cbZaznamyOs_Rok_changed,
                'on_cbSestavyOS_TypDokladu_changed': self.on_cbZaznamyOs_TypDokladu_changed,
                'on_btSestavyOS_DatVyst_clicked': self.on_btSestavyOS_DatVyst_clicked,
                'on_btSestavyOS_DatPlat_clicked': self.on_btSestavyOS_DatPlat_clicked}
        self.wSestavyOSXml.signal_autoconnect(signaly)

        
        self.combo_boxy = ['Mesic', 'Rok', 'TypDokladu']
        self.cbWidgety = {}
        for widget in self.combo_boxy:
            self.cbWidgety[widget] = self.wSestavyOSXml.get_widget("cbSestavyOS_" + widget)

#        self.chWidget_vsichni = self.wSestavyOSXml.get_widget("chSestavyOS_vsichni")
        
        self.btWidget_Ulozit = self.wSestavyOSXml.get_widget("btSestavyOS_Ulozit")

        self.editacni_pole = ['DatVyst', 'DatPlat', 'Vystavil', 'Kod']
        self.edWidgety = {}
        for widget in self.editacni_pole:
            self.edWidgety[widget] = self.wSestavyOSXml.get_widget("eSestavyOS_" + widget)

        self.edWidgety['DatVyst'].set_text(bcas.preved_datum(time.strftime('%d.%m.%Y'),0))
        self.edWidgety['DatPlat'].set_text(bcas.preved_datum(time.strftime('%d.%m.%Y'),0))
        self.edWidgety['Vystavil'].set_text(str(BenedatDB.db.nastaveni(volba="vystavil")[1]))
        self.aktualizace_zobrazeneho_kodu_v_okne_sestav()

        self.tabKlientu = self.wSestavyOSXml.get_widget("twSestavyOS_klienti")
        

        # Nastavení roku a měsíce na aktuální
        self.mesic = time.strftime('%m')
        self.rok = time.strftime('%Y')

#        self.klient = None
#        self.vsichni = True
        self.typ_dokladu = 0
    
        self.klienti = []
        
        # nastavení tabulky klientů
        self.tab_klientu()

#        self.vytvorit_combo_box_klienti()
#        self.chWidget_vsichni.set_active(self.vsichni)

        self.vytvor_cb_mesice()
        self.vytvor_cb_roky()
        self.vytvor_cb_typy_dokladu()



    def tab_klientu(self):
        """načtení widgetu pro tabulku klientů"""
        self.tabKlientu.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        
        self.sloupce_poradi = ['klient']
        self.vytvoreni_list_store_klientu()
        self.vytvoreni_sloupcu_v_tab_klientu()

#        self.vyplnit_klienty_do_tabKlientu()

        


    def vytvoreni_list_store_klientu(self):
        self.klientiList = gtk.ListStore(int, str)
        self.tabKlientu.set_model(self.klientiList)

    def vytvoreni_sloupcu_v_tab_klientu(self):
        self.sloupce = {}
        self.sloupce['klient'] = gtk.TreeViewColumn("Klient",
                gtk.CellRendererText(),
                text=1)
        for sloupec in self.sloupce_poradi:
            self.tabKlientu.append_column(self.sloupce[sloupec])

    def vyplnit_klienty_do_tabKlientu(self):
        klienti_z_db = BenedatDB.db.klienti_id_jmeno(1, pouze='osz', 
                mesic=self.mesic, rok=self.rok)

        setrideny_seznam_klientu = setrideni_slovniku_podle_obsahu(klienti_z_db)

        self.klientiList.clear()
        for klient in setrideny_seznam_klientu: 
            iter = self.klientiList.append()
            self.klientiList.set(iter,
                    0, klient,
                    1, klienti_z_db[klient])
        self.oznac_klienty_v_tabKlientu()

    def oznac_klienty_v_tabKlientu(self):
        self.tabKlientu.get_selection().unselect_all()
        i = 0
        for klient_tmp in self.klientiList:
            id_klienta = klient_tmp[0]

            klient = BenedatDB.db.klient_podle_id(id_klienta)
            if klient[16] == self.typ_dokladu:
                self.tabKlientu.get_selection().select_path(i)
            i += 1

        


    def vytvor_cb_mesice(self):
        """doplnění měsíců do comboboxu"""
        cb = self.cbWidgety['Mesic']
        mesiceList = gtk.ListStore(str, str)
        cb.set_model(mesiceList)
        cell = gtk.CellRendererText()
        cb.pack_start(cell, True)
        cb.add_attribute(cell, 'text', 1)

        mesiceList.clear()
        mesice={'01': 'Leden',
                '02': 'Únor',
                '03': 'Březen',
                '04': 'Duben',
                '05': 'Květen',
                '06': 'Červen',
                '07': 'Červenec',
                '08': 'Srpen',
                '09': 'Září',
                '10': 'Říjen',
                '11': 'Listopad',
                '12': 'Prosinec'}
        mesice_poradi = ['01','02','03','04','05','06',
                '07','08','09','10','11','12']
        for mesic in mesice_poradi:
            iter = mesiceList.append()
            mesiceList.set(iter,
                    0, mesic,
                    1, mesice[mesic])

        cb.set_active(int(self.mesic)-1)

    def on_cbZaznamyOs_Mesic_changed(self, widget):
        """Změna nastavení měsíce"""
        cb = self.cbWidgety['Mesic']
        mesice = cb.get_model()
        index = cb.get_active()
        self.mesic = mesice[index][0]

        self.nastav_citlivost_bt_ulozit()
#        self.vyplnit_klienty_do_combo_boxu()
        self.vyplnit_klienty_do_tabKlientu()
        

    def vytvor_cb_roky(self):
        """doplnění roků do comboboxu"""
        cb = self.cbWidgety['Rok']
        rokyList = gtk.ListStore(str)
        cb.set_model(rokyList)
        cell = gtk.CellRendererText()
        cb.pack_start(cell, True)
        cb.add_attribute(cell, 'text', 0)

        aktualni_rok = self.rok

        rokyList.clear()
        roky_z_db = BenedatDB.db.zaznamy_pouzite_roky()
        roky = []
        for rok in roky_z_db:
            roky.append(rok[0])
#        if not aktualni_rok in roky:
#            roky.append(aktualni_rok)
        
        for rok in roky:
            iter = rokyList.append()
            rokyList.set(iter,
                    0, rok)

        # Zjištění pozice aktuálního roku a jeho vybrání
        i = 0
        for rok in cb.get_model():
            if rok[0] == aktualni_rok:
                break
            else:
                i+=1

        cb.set_active(i)

    def on_cbZaznamyOs_Rok_changed(self, widget):
        """Změna nastavení roku"""
        cb = self.cbWidgety['Rok']
        roky = cb.get_model()
        index = cb.get_active()
        self.rok = roky[index][0]

        self.nastav_citlivost_bt_ulozit()
#        self.vyplnit_klienty_do_combo_boxu()
        self.vyplnit_klienty_do_tabKlientu()


    def vytvor_cb_typy_dokladu(self):
        """doplnění roků do comboboxu"""
        cb = self.cbWidgety['TypDokladu']
        typ_dokladuList = gtk.ListStore(int, str)
        cb.set_model(typ_dokladuList)
        cell = gtk.CellRendererText()
        cb.pack_start(cell, True)
        cb.add_attribute(cell, 'text', 1)

        typ_dokladuList.clear()
        typy_dokladu = {0 : 'Příjmový pokladní doklad',
                        1 : 'Jednoduchý výpis'}
        typy_dokladu_poradi = [0, 1]
        for typ_dokladu in typy_dokladu_poradi:
            iter = typ_dokladuList.append()
            typ_dokladuList.set(iter,
                    0, typ_dokladu,
                    1, typy_dokladu[typ_dokladu])
        cb.set_active(self.typ_dokladu)

    def on_cbZaznamyOs_TypDokladu_changed(self, widget):
        """Změna nastavení typu dokladu"""
        cb = self.cbWidgety['TypDokladu']
        typy_dokladuList = cb.get_model()
        index = cb.get_active()
        self.typ_dokladu = typy_dokladuList[index][0]
        self.oznac_klienty_v_tabKlientu()





    def aktualizace_zobrazeneho_kodu_v_okne_sestav(self):
        """aktualizace zobrazeného kódu v okně sestav"""
        kod_stala_cast = str(BenedatDB.db.nastaveni(volba="kod_stala_cast")[1])
        kod_promenna_cast = str(BenedatDB.db.nastaveni(volba="kod_promenna_cast")[1])
        self.edWidgety['Kod'].set_text(kod_stala_cast + kod_promenna_cast)
                
    def on_wSestavyOS_destroy(self, widget):
        self.destroy()
    
    def on_btSestavyOS_DatVyst_clicked(self, widget):
        datum = dialogKalendar(self.wSestavyOS)
        if datum:
            self.edWidgety['DatVyst'].set_text(datum)

    def on_btSestavyOS_DatPlat_clicked(self, widget):
        datum = dialogKalendar(self.wSestavyOS)
        if datum:
            self.edWidgety['DatPlat'].set_text(datum)

    def on_btSestavyOS_Zavrit_clicked(self, widget):
        self.destroy()

    def callback_selected_foreach(self, treemodel, path, iter):
        id_klienta = self.klientiList.get_value(iter, 0)
        self.klienti.append(id_klienta)



    def on_btSestavyOS_Ulozit_clicked(self, widget):
        datum_vystaveni = self.edWidgety['DatVyst'].get_text()
        datum_platby = self.edWidgety['DatPlat'].get_text()
        vystavil = self.edWidgety['Vystavil'].get_text()
        BenedatDB.db.zmen_nastaveni(volba="vystavil", hodnota=vystavil)
#        BenedatDB.ulozeno = False
        BenedatDB.db.commit()

########################################
        # zpracování označených klientů v tabulce
        (model,pathlist)=self.tabKlientu.get_selection().get_selected_rows()
        self.tabKlientu.get_selection().selected_foreach(self.callback_selected_foreach)
#        print self.klienti

        if self.typ_dokladu == 0:
            sablona_nazvu = 'Prijmovy_pokladni_doklad_'
        else :
            sablona_nazvu = 'Sestava_'
        if len(self.klienti) == 1:
            sablona_nazvu += bez_diakritiky_a_mezer(BenedatDB.db.klient_jmeno_podle_id(self.klienti[0], vystup=2))+"_"

        sablona_nazvu += str(self.mesic) + "_" + str(self.rok) + ".pdf"
        soubor = self.dotaz_ulozeni_sestavy(sablona_nazvu=sablona_nazvu)

        if soubor != -1 and soubor:    
            # Vytvoření sestavy a uložení do souboru
            sestava = bsestavy.Sestavy(BenedatDB.db)
#               print sestava.sestava_text(str(self.klient), str(self.mesic), str(self.rok))
            sestava.sestavy_vyber_pdf(self.klienti, str(self.mesic), str(self.rok), soubor, datum_vystaveni=datum_vystaveni, datum_platby=datum_platby, vystavil=vystavil, typ_dokladu=self.typ_dokladu)

        # zavření okna pro sestavy
        self.destroy()
                
        return
########################################

    def dotaz_ulozeni_sestavy(self, sablona_nazvu=None):
        """Zobrazení a zpracování dialogu pro uložení sestavy vytvořené sestavy"""

        # filtry pro zobrazované soubory
        filtr_pdf = gtk.FileFilter()
        filtr_pdf.add_pattern('*.pdf')


        # xml strom pro dialog
        wUlozeniSestavyXml= gtk.glade.XML(BenedatGladeFile.gladefile, "wUlozeniSestavy")
        self.wUlozeniSestavy = wUlozeniSestavyXml.get_widget("wUlozeniSestavy")

        #nastavení výchozího filtru na db
        self.wUlozeniSestavy.set_filter(filtr_pdf)
        
        self.wUlozeniSestavy.set_do_overwrite_confirmation(True)

        #přednastavení názvu souboru
        if sablona_nazvu:
            self.wUlozeniSestavy.set_current_name(sablona_nazvu)

        navratova_hodnota = self.wUlozeniSestavy.run()
        
        # kontrola vybraného souboru
        if navratova_hodnota == gtk.RESPONSE_OK and self.wUlozeniSestavy.get_filename():
            soubor = self.wUlozeniSestavy.get_filename()
            if os.path.splitext(soubor)[1] != ".pdf":
                soubor += ".pdf"
            self.wUlozeniSestavy.destroy()
            return soubor
        else:
            self.wUlozeniSestavy.destroy()
            return -1

#    def nastav_citlivost_cb_klient(self):
#        self.cbWidgety['Klient'].set_sensitive(not self.vsichni)

    def nastav_citlivost_bt_ulozit(self):
        if BenedatDB.db.klienti_id_jmeno(vystup=1, pouze="osz", mesic=self.mesic, rok=self.rok):
            self.btWidget_Ulozit.set_sensitive(True)
        else:
            self.btWidget_Ulozit.set_sensitive(False)

    def destroy(self):
        self.wSestavyOS.destroy()

    def run(self):
        self.wSestavyOS.show_all()
    
    def nic(self, widget, parametry=None):
        if parametry:
            print parametry    

class BenedatOknoChyba:
    """Okno pro zobrazení chybového hlášení"""
    def __init__(self, text="", text_dalsi="", titulek="Chyba"):
#        self.wChybaXml = gtk.glade.XML(BenedatGladeFile.gladefile, "wChyba")
#        self.wChyba = self.wChybaXml.get_widget("wChyba")
#        self.wChyba.set_property("text", text)
#        self.wChyba.set_property("secondary-text", text_dalsi)
#        self.wChyba.run()
        dialog = gtk.MessageDialog(None,
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,str(text))
        dialog.set_property("secondary-text", text_dalsi)
        dialog.set_property("title", titulek)
        dialog.run()
        dialog.destroy()

def dialogChyba(text="", text_dalsi="", titulek="Chyba"):
    BenedatOknoChyba(text, text_dalsi, titulek)


class BenedatOknoDotaz:
    """Okno pro zobrazení dotazu"""
    def __init__(self, text="", text_dalsi="", titulek="Dotaz"):
#        self.wDotazXml = gtk.glade.XML(BenedatGladeFile.gladefile, "wDotaz")
#        self.wDotaz = self.wDotazXml.get_widget("wDotaz")
#        self.wDotaz.set_property("text", text)
#        self.wDotaz.set_property("secondary-text", text_dalsi)
#        self.wDotaz.run()
        dialog = gtk.MessageDialog(None,
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO,str(text))
        dialog.set_property("secondary-text", text_dalsi)
        dialog.set_property("title", titulek)
        self.navratova_hodnota = dialog.run()
        dialog.destroy()

def dialogDotaz(text="", text_dalsi="", titulek="Dotaz"):
    dialog = BenedatOknoDotaz(text, text_dalsi, titulek)
    return dialog.navratova_hodnota

class BenedatOknoKalendar:
    """Dialogové okno s kalendářem"""
    def __init__(self, predek = None):
        self.aktualni = ""
        self.dialog = gtk.Dialog ("Kalendář", predek,
            gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_MODAL,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK))
        self.kalendar = gtk.Calendar()
        self.dialog.vbox.pack_start(self.kalendar, True, True, 0)
        self.kalendar.connect('day_selected_double_click', self.day_selected_double_click, self.dialog)
        timestamp = time.localtime()
        if timestamp:
            self.kalendar.select_month(timestamp[1] - 1, timestamp[0])
            self.kalendar.select_day(timestamp[2])
        self.dialog.show_all()
        result = self.dialog.run()
        if result == gtk.RESPONSE_OK:
            self.kalendar_kontrola(self.kalendar, self.dialog)
        else:
            self.dialog.destroy()

    def day_selected_double_click(self, widget, dialog):
        self.kalendar_kontrola(widget,dialog)

    def kalendar_kontrola(self, widget, dialog):
        (year, month, day) = widget.get_date()
        self.aktualni = str(day) + '.' + str(month+1) + '.' + str(year)
        self.dialog.destroy()

def dialogKalendar(predek = None):
    """Dialogové okno s kalendářem"""
    kalendar =  BenedatOknoKalendar(predek)
    return kalendar.aktualni

class BenedatOknoNastaveni(BenedatGladeFile, BenedatDB):
    """Okno s nastavením"""
    def __init__(self):
        self.wNastaveniXml = gtk.glade.XML(BenedatGladeFile.gladefile, "wNastaveni")
        self.wNastaveni = self.wNastaveniXml.get_widget("wNastaveni")

        # připojení signálů k událostem
        signaly = { 'on_wNastaveni_destroy': self.destroy,
                    'on_btNastaveni_pouzit_clicked': self.btNastaveni_pouzit,
                    'on_btNastaveni_zrusit_clicked': self.btNastaveni_zrusit, 
                    'on_btNastaveni_ulozit_clicked': self.btNastaveni_ulozit}
        self.wNastaveniXml.signal_autoconnect(signaly)

        # načtení editačních polí
        self.editacni_pole= ['cestovne_os_cena_za_litr',
                        'cestovne_os_exp',
                        'cestovne_os_k',
                        'cestovne_os_nastupni_sazba',
                        'cestovne_os_podil_klienta',
                        'kod_stala_cast',
                        'kod_promenna_cast',
                        'dolni_hranice_poctu_hodin',
                        'horni_hranice_poctu_hodin',
                        'adresa',
                        'adresa_dalsi',
                        'pokladna',
                        'os_cena_obeda',
                        'os_cena_prenocovani']
        
        self.edWidgety = {}
        for pole in self.editacni_pole:
            self.edWidgety[pole] = self.wNastaveniXml.get_widget("eNastaveni_" + pole)
#            print self.edWidgety[pole], pole
        self.nacteni_hodnot_z_db()
        
    def btNastaveni_zrusit(self, widget):
        self.destroy()

    def btNastaveni_pouzit(self, widget):
        self.ulozeni_hodnot_do_db()
        self.nacteni_hodnot_z_db()

    def btNastaveni_ulozit(self, widget):
        self.ulozeni_hodnot_do_db()
        self.destroy()
        
    def run(self):
        self.wNastaveni.show_all()

    def nic(self, widget, parametry=None):
        if parametry:
            print parametr

    def destroy(self, widget=None):
        self.wNastaveni.destroy()
    
    def nacteni_hodnot_z_db(self):
        """Načtení hodnot z databáze do editačních polí"""
        nastaveni = BenedatDB.db.nastaveni_slovnik()
        for key in self.editacni_pole:
            if(key in nastaveni):
                self.edWidgety[key].set_text(nastaveni[key][0])
            else :
                self.edWidgety[key].set_text('')

    def ulozeni_hodnot_do_db(self):
        """Uložení zeditovaných hodnot do databáze"""
        nastaveni_z_db = BenedatDB.db.nastaveni_slovnik()
        nastaveni_z_form = {}
        for key in self.editacni_pole:
            nastaveni_z_form[key] = self.edWidgety[key].get_text()

        for key in nastaveni_z_form.keys():
            if key in nastaveni_z_db:
                if nastaveni_z_db[key][0] != nastaveni_z_form[key]:
                    BenedatDB.db.zmen_nastaveni(key, nastaveni_z_form[key])
            else :
                BenedatDB.db.pridej_nastaveni(key, nastaveni_z_form[key])
        BenedatDB.ulozeno = False
        self.uloz_db()

def setrideni_slovniku_podle_obsahu(slovnik):
    """Setřídění slovníku podle hodnot - vrátí seznam klíčů"""
    if os.name == 'nt':
        locale.setlocale(locale.LC_ALL,'')
    else:
        locale.setlocale(locale.LC_ALL,'cs_CZ.utf8')

    slovnik_obraceny = {}
    for k in slovnik.keys():
        slovnik_obraceny[slovnik[k]] = k
    setrideny = []
    trideni = slovnik_obraceny.keys()
    trideni.sort(locale.strcoll)
    for t in trideni:
        setrideny.append(slovnik_obraceny[t])

    return setrideny
    
    

def float_or_zero(arg):
  try:
    arg = float(arg.replace(',', '.'))
  except ValueError, err:
    arg = 0
  return arg

def bez_none(text):
    if text == None:
        return ""
    else:
        return str(text)

def bez_diakritiky_a_mezer(text):
    tmp = unicodedata.normalize('NFKD', text)
    text = ''
    for c in tmp:
        if not unicodedata.combining(c):
            if c == " ":
                pass
#                text += "_"    
            else :
                text += c
    return text



if __name__ == "__main__":
    benedat = BenedatHlavniOkno()
    gtk.main()





