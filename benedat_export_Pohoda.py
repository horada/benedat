#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""Modul pro export dat do Pohody"""

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


import xml.dom.minidom as xml
import sys
from StringIO import StringIO
import benedat_config as bconf




class Souhrn_ucetnictvi(dict):
    """Třída pro vytvoření souhrnu pro účetnictvi"""
    def __init__(self, soubor):
        self.soubor = soubor

    def __str__(self):
        """funkce pro tisk souhrnu"""
        klice=self.keys()
        klice.sort()
        tmp = ""
        for polozka in klice:
            tmp += self[polozka].__str__()
        return tmp
        
    def uloz(self):
        souborovyobjekt = open(self.soubor, "w")
        souborovyobjekt.write("Kód\t\tDatum\t\tPlátce\t\tČástka\t\tText\n")
        souborovyobjekt.write(self.__str__().encode("utf8"))
        souborovyobjekt.close()

class Souhrn_polozka():
    """Třída pro souhrn jednoho klienta"""
    def __init__(self):
        self.kod_stala_cast = ""
        self.kod_promenna_cast = ""
        self.datum_vystaveni = ""
        self.datum_platby = ""
        self.platce = ""
        self.text = ""
        self.cena = ""

    def __str__(self):
        """Funkce pro výpis"""
        tmp = u""
        tmp += (self.kod_stala_cast+str(self.kod_promenna_cast)).ljust(8)
        tmp += "\t"
        tmp += self.datum_vystaveni.ljust(8)
        tmp += "\t"
#        print self.platce
        tmp += self.platce.ljust(8)
        tmp += "\t"
        tmp += str(self.cena).ljust(8)
        tmp += "\t"
        tmp += self.text
        tmp += "\n" 
        return tmp 


class xmlDokument(xml.Document):
    """Třída pro celý xml dokument"""
    def __init__(self, id):
        self.__nacteni_konfigurace_ze_souboru()
        xml.Document.__init__(self)
        self.__vytvor_dataPack(id=id)

    def __nacteni_konfigurace_ze_souboru(self, soubor="benedat.conf"):
        """Načtení některých konfiguračních voleb ze souboru"""
        # načtení/vytvoření konfigurace 
        self.konf = bconf.Konfigurace(soubor)
        self.konf.nacteni_konfigurace_ze_souboru()

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
            if not self.konf.volba(volba):
                self.konf[volba] = default_konf_volby[volba]




    def __vytvor_dataPack(self, id):
        """vytvoření kořenového xml elementu"""
        # Hlavní element celého dokumentu
        self.dataPack = self.createElement("dat:dataPack")
        self.dataPack.setAttribute('version', '1.0')
        self.dataPack.setAttribute('id', id)
        self.dataPack.setAttribute('ico', self.konf.volba('ico'))
        self.dataPack.setAttribute('application', self.konf.volba('aplikace'))
        self.dataPack.setAttribute('note', self.konf.volba('poznamka_k_exportu'))
        self.dataPack.setAttribute('xmlns:dat', 'http://www.stormware.cz/schema/data.xsd')
        self.dataPack.setAttribute('xmlns:vch', 'http://www.stormware.cz/schema/voucher.xsd')
        self.dataPack.setAttribute('xmlns:typ', 'http://www.stormware.cz/schema/type.xsd')
        self.appendChild(self.dataPack)
        

    def pridani_dokladu(self, id, id_dokladu, kod_promenna_cast, kod_stala_cast,
                        datum_vystaveni, datum_platby, text, jmeno, adresa, cena ):
        """Metoda pro přidání jednoho dokladu"""
        
        if type(id)==unicode:
            id = id.encode("utf-8")
        if type(id_dokladu)==unicode:
            id_dokladu = id_dokladu.encode("utf-8")
        if type(kod_promenna_cast)==unicode:
            kod_promenna_cast = kod_promenna_cast.encode("utf-8")
        if type(kod_stala_cast)==unicode:
            kod_stala_cast = kod_stala_cast.encode("utf-8")
        if type(datum_vystaveni)==unicode:
            datum_vystaveni = datum_vystaveni.encode("utf-8")
        if type(datum_platby)==unicode:
            datum_platby = datum_platby.encode("utf-8")
        if type(text)==unicode:
            text = text.encode("utf-8")
        if type(jmeno)==unicode:
            jmeno = jmeno.encode("utf-8")
        if type(adresa)==unicode:
            adresa = adresa.encode("utf-8")
        if type(cena)==unicode:
            cena = cena.encode("utf-8")

#        print "id:\t",
#        print type(id)
#        print "id_dokladu:\t",
#        print type(id_dokladu)
#        print "kod_promenna_cast:\t",
#        print type(kod_promenna_cast)
#        print "kod_stala_cast:\t",
#        print type(kod_stala_cast)
#        print "datum_vystaveni:\t",
#        print type(datum_vystaveni)
#        print "datum_platby:\t",
#        print type(datum_platby)
#        print "text:\t",
#        print type(text)
#        print "jmeno:\t",
#        print type(jmeno)
#        print "adresa:\t",
#        print type(adresa)
#        print "cena:\t",
#        print type(cena)

        
        # hlavní element jednoho dokladu
        dat_dataPackItem = self.createElement("dat:dataPackItem")
        dat_dataPackItem.setAttribute('version','1.0')
        dat_dataPackItem.setAttribute('id',id)
        self.dataPack.appendChild(dat_dataPackItem)

        # celý doklad
        vch_voucher = self.createElement("vch:voucher")
        vch_voucher.setAttribute('version', '1.3')
        dat_dataPackItem.appendChild(vch_voucher)

        # Hlavička dokladu
        vch_voucherHeader = self.createElement("vch:voucherHeader")
        vch_voucher.appendChild(vch_voucherHeader)

        # id dokladu
        vch_id = self.createElement("vch:id")
        vch_id.appendChild(self.createTextNode(id_dokladu))
        vch_voucherHeader.appendChild(vch_id)

        # typ dokladu (příjmový)
        vch_voucherType = self.createElement("vch:voucherType")
        vch_voucherType.appendChild(self.createTextNode("receipt"))
        vch_voucherHeader.appendChild(vch_voucherType)

        # kód pokladny
        vch_cashAccount = self.createElement("vch:cashAccount")
        vch_voucherHeader.appendChild(vch_cashAccount)
        typ_ids = self.createElement("typ:ids")
        typ_ids.appendChild(self.createTextNode(self.konf.volba('pokladna')))
        vch_cashAccount.appendChild(typ_ids)

        # kód dokladu
        vch_number = self.createElement("vch:number")
        vch_voucherHeader.appendChild(vch_number)
        # proměnná část kódu
#        typ_id = self.createElement("typ:id")
#        typ_id.appendChild(self.createTextNode(kod_promenna_cast))
#        vch_number.appendChild(typ_id)
        # stálá část kódu
#        typ_ids = self.createElement("typ:ids")
#        typ_ids.appendChild(self.createTextNode(kod_stala_cast))
#        vch_number.appendChild(typ_ids)
        # kontrola duplicity dokladu
        typ_numberRequested = self.createElement("typ:numberRequested")
        typ_numberRequested.setAttribute("true")
        typ_numberRequested.appendChild(self.createTextNode(str(kod_stala_cast) + str(kod_promenna_cast)))
        vch_number.appendChild(typ_numberRequested)
        
        # datum vystavení
        vch_date = self.createElement("vch:date")
        vch_date.appendChild(self.createTextNode(datum_vystaveni))
        vch_voucherHeader.appendChild(vch_date)
        
        # datum platby
        if datum_platby:
            vch_datePayment = self.createElement("vch:datePayment")
            vch_datePayment.appendChild(self.createTextNode(datum_platby))
            vch_voucherHeader.appendChild(vch_datePayment)

        # předkontace
        vch_accounting = self.createElement("vch:accounting")
        vch_voucherHeader.appendChild(vch_accounting)
        # kód předkontace
        typ_accountingType = self.createElement("typ:ids")
        typ_accountingType.appendChild(self.createTextNode(self.konf.volba('kod_predkontace')))
        vch_accounting.appendChild(typ_accountingType)

        # členění dph
        vch_classificationVAT = self.createElement("vch:classificationVAT")
        vch_voucherHeader.appendChild(vch_classificationVAT)
        # kód členění dph
        typ_classificationVATType = self.createElement("typ:classificationVATType")
        typ_classificationVATType.appendChild(self.createTextNode(self.konf.volba('kod_cleneni_dph')))
        vch_classificationVAT.appendChild(typ_classificationVATType)

        # text dokladu
        vch_text = self.createElement("vch:text")
        vch_text.appendChild(self.createTextNode(text))
        vch_voucherHeader.appendChild(vch_text)

        # identifikace zákazníka 
        vch_partnerIdentity = self.createElement("vch:partnerIdentity")
        vch_voucherHeader.appendChild(vch_partnerIdentity)

        # adresa
        typ_address = self.createElement("typ:address")
        vch_partnerIdentity.appendChild(typ_address)
        # firma
        typ_company = self.createElement("typ:company")
        typ_company.appendChild(self.createTextNode(jmeno))
        typ_address.appendChild(typ_company)
        # jméno
        typ_name = self.createElement("typ:name")
        typ_name.appendChild(self.createTextNode(jmeno))
        typ_address.appendChild(typ_name)
        # ulice
        typ_street = self.createElement("typ:street")
        typ_street.appendChild(self.createTextNode(adresa))
        typ_address.appendChild(typ_street)
        
        # středisko
        vch_centre = self.createElement("vch:centre")
        vch_voucherHeader.appendChild(vch_centre)
        # kód střediska
        typ_centre_ids= self.createElement("typ:ids")
        typ_centre_ids.appendChild(self.createTextNode(self.konf.volba('kod_strediska')))
        vch_centre.appendChild(typ_centre_ids)
        
        # činnost
        vch_activity = self.createElement("vch:activity")
        vch_voucherHeader.appendChild(vch_activity)
        # kód činnosti
        typ_activity_ids= self.createElement("typ:ids")
        typ_activity_ids.appendChild(self.createTextNode(self.konf.volba('kod_cinnosti')))
        vch_activity.appendChild(typ_activity_ids)
        
        # souhrn dokladu
        vch_voucherSummary = self.createElement("vch:voucherSummary")
        vch_voucher.appendChild(vch_voucherSummary)
        # cena
        vch_homeCurrency = self.createElement("vch:homeCurrency")
        vch_voucherSummary.appendChild(vch_homeCurrency)
        typ_priceNone = self.createElement("typ:priceNone")
        typ_priceNone.appendChild(self.createTextNode(cena))
        vch_homeCurrency.appendChild(typ_priceNone)

    def to_xml(self, debug=False):
        """Převede na xml"""
        writer = StringIO()
        # pokud je debug True bude výpis odsazovaný
        if debug:
            self.writexml(writer,  indent="", addindent="\t", newl="\n", encoding="Windows-1250")
        else:
            self.writexml(writer,  indent="", addindent="", newl="", encoding="Windows-1250")
#        print writer.getvalue()
#        return writer.getvalue()
        return writer.getvalue().decode("utf-8").encode("cp1250")

    def to_xml_soubor(self, soubor="Sestava.xml", debug=False):
        """Uloží do xml souboru"""
        souborovyobjekt = open(soubor, "w")
        souborovyobjekt.write(self.to_xml(debug))
        souborovyobjekt.close()





def test():
    """testovací vytvoření xml"""
    doc = xmlDokument(id="BD09")
    doc.pridani_dokladu(id="29HP5037", id_dokladu="9999",
            kod_promenna_cast="5037", kod_stala_cast="29HP",
            datum_vystaveni="2009-09-21", datum_platby="2009-09-21",
            text="Účtujeme Vám za odlehčovací službu - 09/2009",
            jmeno="František Trávníček", adresa="Horní Dolní 232",
            cena="1313")

    doc.to_xml_soubor("Sestava.xml", True)
#    doc.to_xml_soubor("Sestava.xml")


#    doc = xml.Document()
#    dat_dataPack = doc.createElement("dat:dataPack")
#    dat_dataPack.setAttribute('version', '1.0')
#    dat_dataPack.setAttribute('id', 'BD09')
#    dat_dataPack.setAttribute('ico', '0000')
#    dat_dataPack.setAttribute('application', 'BeneDat')
#    dat_dataPack.setAttribute('note', 'Odlehčovací služba')
#    dat_dataPack.setAttribute('xmlns:dat', 'http://www.stormware.cz/schema/data.xsd')
#    dat_dataPack.setAttribute('xmlns:vch', 'http://www.stormware.cz/schema/voucher.xsd')
#    dat_dataPack.setAttribute('xmlns:typ', 'http://www.stormware.cz/schema/type.xsd')
#    doc.appendChild(dat_dataPack)

#    dat_dataPackItem = doc.createElement("dat:dataPackItem")
#    dat_dataPackItem.setAttribute('version','1.0')
#    dat_dataPackItem.setAttribute('id','1223')
#    dat_dataPack.appendChild(dat_dataPackItem)

#    vch_voucher = doc.createElement("vch:voucher")
#    vch_voucher.setAttribute('version', '1.3')
#    dat_dataPackItem.appendChild(vch_voucher)

#    vch_voucherHeader = doc.createElement("vch:voucherHeader")
#    vch_voucher.appendChild(vch_voucherHeader)
#    
#    vch_id = doc.createElement("vch:id")
#    vch_id.appendChild(doc.createTextNode("1001"))
#    vch_voucherHeader.appendChild(vch_id)

#    vch_voucherType = doc.createElement("vch:voucherType")
#    vch_voucherType.appendChild(doc.createTextNode("receipt"))
#    vch_voucherHeader.appendChild(vch_voucherType)

#    vch_cashAccount = doc.createElement("vch:cashAccount")
#    vch_voucherHeader.appendChild(vch_cashAccount)
#    
#    typ_ids = doc.createElement("typ:ids")
#    typ_ids.appendChild(doc.createTextNode("HP"))
#    vch_cashAccount.appendChild(typ_ids)

#    vch_number = doc.createElement("vch:number")
#    vch_voucherHeader.appendChild(vch_number)

#    typ_id = doc.createElement("typ:id")
#    typ_id.appendChild(doc.createTextNode("1001"))
#    vch_number.appendChild(typ_id)
#    
#    typ_ids = doc.createElement("typ:ids")
#    typ_ids.appendChild(doc.createTextNode("29HP"))
#    vch_number.appendChild(typ_ids)

#    vch_date = doc.createElement("vch:date")
#    vch_date.appendChild(doc.createTextNode("2009-09-17"))
#    vch_voucherHeader.appendChild(vch_date)

#    vch_datePayment = doc.createElement("vch:datePayment")
#    vch_datePayment.appendChild(doc.createTextNode("2009-09-17"))
#    vch_voucherHeader.appendChild(vch_datePayment)

#    vch_classificationVAT = doc.createElement("vch:classificationVAT")
#    vch_voucherHeader.appendChild(vch_classificationVAT)

#    typ_classificationVATType = doc.createElement("typ:classificationVATType")
#    typ_classificationVATType.appendChild(doc.createTextNode("nonSubsume"))
#    vch_classificationVAT.appendChild(typ_classificationVATType)

#    vch_text = doc.createElement("vch:text")
#    vch_text.appendChild(doc.createTextNode("Účtujeme Vám za odlehčovací službu 09/2009"))
#    vch_voucherHeader.appendChild(vch_text)

#    vch_partnerIdentity = doc.createElement("vch:partnerIdentity")
#    vch_voucherHeader.appendChild(vch_partnerIdentity)

#    typ_address = doc.createElement("typ:address")
#    vch_partnerIdentity.appendChild(typ_address)

#    typ_name = doc.createElement("typ:name")
#    typ_name.appendChild(doc.createTextNode("Horák Daniel"))
#    typ_address.appendChild(typ_name)

#    typ_street = doc.createElement("typ:street")
#    typ_street.appendChild(doc.createTextNode("Horní Krupá 112|Havlíčkův Brod 580 01"))
#    typ_address.appendChild(typ_street)

#    vch_voucherSummary = doc.createElement("vch:voucherSummary")
#    vch_voucher.appendChild(vch_voucherSummary)

#    vch_homeCurrency = doc.createElement("vch:homeCurrency")
#    vch_voucherSummary.appendChild(vch_homeCurrency)

#    typ_priceNone = doc.createElement("typ:priceNone")
#    typ_priceNone.appendChild(doc.createTextNode("1324"))
#    vch_homeCurrency.appendChild(typ_priceNone)

#    



#    writer = StringIO()
#    doc.writexml(writer,  indent="", addindent="", newl="", encoding="Windows-1250")
##    print writer.getvalue()
##    print writer.getvalue().decode("utf-8").encode("cp1250")
#    souborovyobjekt = open("Sestava.xml", "w")
#    souborovyobjekt.write(writer.getvalue().decode("utf-8").encode("cp1250"))
#    souborovyobjekt.close()
#    



if __name__ == "__main__":
    test()




#<?xml version="1.0" encoding="Windows-1250"?>

#<dat:dataPack version="1.0" id="BD09" ico="0000" application="BeneDat" note="Odlehčovací služba" 
#xmlns:dat="http://www.stormware.cz/schema/data.xsd" 
#xmlns:vch="http://www.stormware.cz/schema/voucher.xsd" 
#xmlns:typ="http://www.stormware.cz/schema/type.xsd" >
#    
#    <!-- Pokladní doklad bez položek -->
#    <dat:dataPackItem version="1.0" id="1221">
#        <vch:voucher version="1.3">
#            <vch:voucherHeader>
#                <vch:id>1001</vch:id>
#                <vch:voucherType>receipt</vch:voucherType>
#                <vch:cashAccount>
#                    <typ:ids>HP</typ:ids>
#                </vch:cashAccount>
#                <vch:number>
#                    <typ:id>1001</typ:id>
#                    <typ:ids>29HP</typ:ids>
#                </vch:number>
#                <vch:date>2009-09-15</vch:date>
#                <vch:datePayment>2009-09-15</vch:datePayment>
#                <vch:classificationVAT>
#                    <typ:classificationVATType>nonSubsume</typ:classificationVATType>
#                </vch:classificationVAT>
#                <vch:text>Účtujeme Vám za odlehčovací službu 09/2009</vch:text>
#                <vch:partnerIdentity>
#                    <typ:address>
#                        <typ:name>Horák Daniel</typ:name>
#                        <typ:street>Horní Krupá 112|Havlíčkův Brod 580 01</typ:street>
#                    </typ:address>
#                </vch:partnerIdentity>
#            </vch:voucherHeader>
#            <vch:voucherSummary>
#                <vch:homeCurrency>
#                    <typ:priceNone>1234</typ:priceNone>
#                </vch:homeCurrency>
#            </vch:voucherSummary>
#        </vch:voucher>
#    </dat:dataPackItem>
#    

#        
#</dat:dataPack>

