#!/usr/bin/env python
#-*- coding: utf-8 -*- 
"""
Gui for BeneDat.

VARIABLES:

FUNCTIONS:

CLASSES:

"""
#
# BeneDat - program pro výpočet ceny a vytvoření souhrnu za poskytnuté služby 
#           klientům občanského sdružení BENEDIKTUS (podpora lidí s postižením)
# BeneDat - program for prices calculation and summary creation of utilized 
#           services for clients of Civic association BENEDIKTUS 
#           (supports people with disabilities)
#
# This file is part of BeneDat.
#
# BeneDat is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BeneDat is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BeneDat.  If not, see <http://www.gnu.org/licenses/>.
#


GLADEFILE="gui/bd_gui.glade"


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
#    import pango
except:
    print "ERROR: Import module gtk or gtk.glade failed."
    sys.exit(1)

import os
import time
from pprint import pprint

import bd_config
import bd_clients
import bd_database
import bd_datetime
from bd_datetime import Time, Date
from bd_descriptions import eSettings,teSettings
import bd_logging
from bd_logging import rnl
import bd_records





# get configuration
conf = bd_config.getConfig()
# get logger
log = bd_logging.getLogger(__name__)

# database
db = None
_last_open_file = conf.get('main', 'last_open_file', None)
if _last_open_file:
    # open last opened database file
    if os.path.isfile(_last_open_file):
        db = bd_database.getDb(db_file=_last_open_file)
    else:
        conf.set('main', 'last_open_file', '')



import bd_summary

class WMain():
    """
    BeneDat main window (guidepost).
    """
    def __init__(self):
        self.wxml = gtk.glade.XML(GLADEFILE, "wMain")

        signals = { 
                "on_wMain_destroy": self.exit,
                "on_wMain_btRecords_clicked": self.openWRecords,
                "on_wMain_btSummary_clicked": self.openWSummary,
                "on_wMain_btClients_clicked": self.openWClients,
                "on_wMain_btNewDb_clicked": self.dialogNewDb,
                "on_wMain_btOpenDb_clicked": self.dialogOpenDb,
                "on_wMain_btEmptyDbCopy_clicked": self.dialogEmptyDbCOpy,
                "on_wMain_btCloseDb_clicked": self.closeDb,
                "on_wMain_btSettings_clicked": self.openWSettings,
                "on_wMain_btExit_clicked": self.exit,
                }
        self.wxml.signal_autoconnect(signals)

        # Widgets
        widgets = (
                "btRecords",
                "btSummary",
                "btClients",
                "btNewDb",
                "btOpenDb",
                "btEmptyDbCopy",
                "btCloseDb",
                "btSettings",
                "btExit",
                "statusbar",
                )
        self.allWidgets = {}
        for widget in widgets:
            self.allWidgets[widget] = self.wxml.get_widget("wMain_%s" % widget)


        self.fillStatusbar()
        self.setSensitivity()


    def exit(self, widget):
        """
        Exit BeneDat.
        """
        db.commit()
        log.debug('gtk.main_quit()')
        gtk.main_quit()

    def openWRecords(self, widget):
        """
        Open window for records.
        """
        log.debug('openWRecords()')
        windowRecords = WRecords()
        windowRecords.run()

    def openWSummary(self, widget):
        """
        Open window for summary.
        """
        log.debug('openWSummary()')
        windowSummary = WSummary()
        windowSummary.run()

    def openWClients(self, widget):
        """
        Open window for clients.
        """
        log.debug('openWClients()')
        windowClients = WClients()
        windowClients.run()

    def openWSettings(self, widget):
        """
        Open window for settings.
        """
        log.debug('openWSettings()')
        windowSettings = WSettings()
        windowSettings.run()

    def dialogNewDb(self, widget):
        """
        Open dialog for new db.
        """
        log.debug('dialogNewDb()')
        global db
        
        # filters for listed files in dialog
        file_filter = {}
        file_filter['db'] = gtk.FileFilter()
        file_filter['db'].add_pattern('*.db')
        file_filter['vse'] = gtk.FileFilter()
        file_filter['vse'].add_pattern('*')

        # change filter of listed files
        def on_wNewDB_cbFileType_changed(widget, data=None):
            if wNewDB_cbFileType.get_active() == 0:
                self.wNewDB.set_filter(file_filter['db'])
            else:
                self.wNewDB.set_filter(file_filter['vse'])
                

        # xml tree for dialog
        wNewDBxml = gtk.glade.XML(GLADEFILE, "wNewDB")
        self.wNewDB = wNewDBxml.get_widget("wNewDB")
        # box for chose type of file
        wNewDB_cbFileType = wNewDBxml.get_widget("wNewDB_cbFileType")
        # fulfilment of box for file type selection
        ls_model = gtk.ListStore(str)
        ls_model.append(["Pouze databázové soubory (*.db)"])
        ls_model.append(["Všechny soubory"])
        wNewDB_cbFileType.set_model(ls_model)
        cell = gtk.CellRendererText()
        wNewDB_cbFileType.pack_start(cell)
        wNewDB_cbFileType.add_attribute(cell,'text',0)
        wNewDB_cbFileType.set_active(0)
        # connect signal for change
        wNewDB_cbFileType.connect('changed', on_wNewDB_cbFileType_changed)
        # set default filter to 'db'
        self.wNewDB.set_filter(file_filter['db'])   

        # run dialog
        returned_value = self.wNewDB.run()
        
        # check selected file
        if returned_value == gtk.RESPONSE_OK and self.wNewDB.get_filename():
            file_name = self.wNewDB.get_filename().decode("utf-8")
            if os.path.splitext(file_name)[1] != ".db":
                file_name += ".db"
            conf.set('main', 'last_open_file', file_name)
            log.info("Creating db %s" % conf.get('main', 'last_open_file'))

            self.wNewDB.destroy()

            # create new db
            db =  bd_database.getDb(db_file=conf.get('main', 'last_open_file'),
                    new=True)
        else:
            self.wNewDB.destroy()
        self.fillStatusbar()
        self.setSensitivity()


    def dialogOpenDb(self, widget):
        """
        Open dialog for open db.
        """
        log.debug('dialogOpenDb()')
        global db

        # filters for listed files in dialog
        file_filter = {}
        file_filter['db'] = gtk.FileFilter()
        file_filter['db'].add_pattern('*.db')
        file_filter['vse'] = gtk.FileFilter()
        file_filter['vse'].add_pattern('*')

        # change filter of listed files
        def on_wOpenDB_cbFileType_changed(widget, data=None):
            if wOpenDB_cbFileType.get_active() == 0:
                self.wOpenDB.set_filter(file_filter['db'])
            else:
                self.wOpenDB.set_filter(file_filter['vse'])
                
        
        # xml tree for dialog
        wOpenDBxml = gtk.glade.XML(GLADEFILE, "wOpenDB")
        self.wOpenDB = wOpenDBxml.get_widget("wOpenDB")
        # box for chose type of file
        wOpenDB_cbFileType = wOpenDBxml.get_widget("wOpenDB_cbFileType")
        # fulfilment of box for file type selection
        ls_model = gtk.ListStore(str)
        ls_model.append(["Pouze databázové soubory (*.db)"])
        ls_model.append(["Všechny soubory"])
        wOpenDB_cbFileType.set_model(ls_model)
        cell = gtk.CellRendererText()
        wOpenDB_cbFileType.pack_start(cell)
        wOpenDB_cbFileType.add_attribute(cell,'text',0)
        wOpenDB_cbFileType.set_active(0)
        # connect signal for change
        wOpenDB_cbFileType.connect('changed', on_wOpenDB_cbFileType_changed)
        # set default filter to 'db'
        self.wOpenDB.set_filter(file_filter['db'])   

        # run open dialog
        returned_value = self.wOpenDB.run()
        
        # check selected file
        if returned_value == gtk.RESPONSE_OK and self.wOpenDB.get_filename():
            conf.set('main', 'last_open_file', 
                    self.wOpenDB.get_filename().decode("utf-8"))
            log.info("Open database %s" % conf.get('main', 'last_open_file'))
            self.wOpenDB.destroy()
            # Open db
            if db:
                db.open_database(db_file=conf.get('main', 'last_open_file'))
            else:
                db = bd_database.getDb(db_file=conf.get('main', 'last_open_file'))
        else:
            self.wOpenDB.destroy()
        self.fillStatusbar()
        self.setSensitivity()
    



    def dialogEmptyDbCOpy(self, widget):
        """
        Open dialog for copy empty db.
        """
        log.debug('dialogEmptyDbCOpy()')
        pass

    def closeDb(self, widget):
        """
        Close opened database.
        """
        global db
        log.debug('closeDb()')
        db = None
        conf.set('main', 'last_open_file', None)
        self.fillStatusbar()
        self.setSensitivity()

    def fillStatusbar(self, text=None):
        if not text:
            text = "...%s" % conf.get('main', 'last_open_file', '')[-30:]
        self.allWidgets['statusbar'].push(0, str(text))

    def setSensitivity(self):
        """
        Set sensitivity of buttons (related to DB).
        """
        global  db
        if db:
            sensitivity = True
        else:
            sensitivity = False
        buttons = (
                "btRecords",
                "btSummary",
                "btClients",
                "btCloseDb",
                "btEmptyDbCopy",
                "btSettings",
                )
        for bt in buttons:
            self.allWidgets[bt].set_property("sensitive", sensitivity)



class WClients():
    """
    BeneDat clients window.
    """
    def __init__(self):
        # Actual client
        self.actual_client = None

        # Window 
        self.wxml = gtk.glade.XML(GLADEFILE, "wClients")
        self.w = self.wxml.get_widget("wClients")
        
        # Signals
        signals = {
                "on_wClients_destroy": self.nothing,
                "on_wClients_btNewClient_clicked": self.newClient,
                "on_wClients_btDeleteClient_clicked": self.deleteClient,
                "on_wClients_btSaveClient_clicked": self.saveClient,
                "on_wClients_btClose_clicked": self.closeWClients,
                "on_wClients_chOS_toggled": self.chOStoggled,
                "on_wClients_chChB_toggled": self.chChBtoggled,
                }
        self.wxml.signal_autoconnect(signals)

        # Widgets
        self.allWidgets = {}
        widgets = (
                'eFirstName',
                'eLastName',
                'eAddress',
                'ePhone',
                'eMobilePhone1',
                'eMobilePhone2',
                'eNotes',
                'eDistance',
                'cbDocumentType',
                'chOS',
                'chSTD',
                'chChB',
                'tvClientsTable',
                'exOS',
                'exChB',
                'eOSMonthRate',
                'eOSMonthHoursRate',
                'eOSHoursRate1',
                'eOSHoursRate2',
                'eOSHoursRate3',
                'eChBMonthRate',
                'eChBMonthHoursRate',
                'eChBHoursRate1',
                'eChBHoursRate2',
                'eChBHoursRate3',
                )
        for widget in widgets:
            self.allWidgets[widget] = self.wxml.get_widget("wClients_%s"%widget)

        # connect signal for select row by simple click
        self.allWidgets['tvClientsTable'].get_selection().connect('changed',self.cursorChanged)

        # prepare document type combobox
        self.prepareComboBoxDocumentType()

        # Prepare and fill table of clients
        self.prepareClientsTable()
        # sort records table by client
        self.clientsListStore.set_sort_column_id(1, gtk.SORT_ASCENDING)
        self.clientsListStore.set_sort_column_id(2, gtk.SORT_ASCENDING)

        # put cursor to the FirstName field
        self.allWidgets['eFirstName'].grab_focus()

    def run(self):
        log.debug("<wClients>.w.show_all()"%self)
        self.w.show_all()
        
    def prepareComboBoxDocumentType(self):
        log.debug("prepareComboBoxDocumentType()")
        self.documentTypeListStore = gtk.ListStore(str, str)
        self.allWidgets['cbDocumentType'].set_model(self.documentTypeListStore)
        cell = gtk.CellRendererText()
        self.allWidgets['cbDocumentType'].pack_start(cell, True)
        self.allWidgets['cbDocumentType'].add_attribute(cell, 'text', 1)
        self.fillComboBoxDocumentType()


    def fillComboBoxDocumentType(self,document_type = "PPD"):
        log.debug("fillComboBoxDocumentType()")
        self.documentTypeListStore.clear()
        document_types = {
                'PPD': "Příjmový pokladní doklad",
                'JV': "Jednoduchý výpis",
                }
        dkeys = document_types.keys()
        for type_ in dkeys:
            self.documentTypeListStore.append([type_, document_types[type_]])
        i = 0
        for t in self.documentTypeListStore:
            if t[0] == document_type:
                break
            else:
                i+=1
        self.allWidgets['cbDocumentType'].set_active(i)





    def prepareClientsTable(self):
        """
        Prepare and fill table of clients.
        """
        # 
        self.clientsListStore = gtk.ListStore(
                int, # id
                str, # LastName
                str, # firstName
                str, # address
                str, # phone
                str, # mobilePhone1
                str, # mobilePhone2
                str, # notes
                int, # eDistance
                )
        self.allWidgets['tvClientsTable'].set_model(self.clientsListStore)

        columns = {}
        columns['id'] = gtk.TreeViewColumn("ID",
                gtk.CellRendererText(),
                text=0)
        columns['firstName'] = gtk.TreeViewColumn("Jméno",
                gtk.CellRendererText(),
                text=1)
        columns['lastName'] = gtk.TreeViewColumn("Příjmení",
                gtk.CellRendererText(),
                text=2)
        columns['address'] = gtk.TreeViewColumn("Adresa",
                gtk.CellRendererText(),
                text=3)
        columns['phone'] = gtk.TreeViewColumn("Telefon",
                gtk.CellRendererText(),
                text=4)
        columns['mobilePhone1'] = gtk.TreeViewColumn("Mobil 1",
                gtk.CellRendererText(),
                text=5)
        columns['mobilePhone2'] = gtk.TreeViewColumn("Mobil 2",
                gtk.CellRendererText(),
                text=6)
        columns['notes'] = gtk.TreeViewColumn("Poznámka",
                gtk.CellRendererText(),
                text=7)
        columns['eDistance'] = gtk.TreeViewColumn("Vzdálenost",
                gtk.CellRendererText(),
                text=8)

        columns_order = (
                'id',
                'lastName',
                'firstName',
                'address',
                'phone',
                'mobilePhone1',
                'mobilePhone2',
                'notes',
                'eDistance',
                )
        for column in columns_order:
            self.allWidgets['tvClientsTable'].append_column(columns[column])
        
        # configure sorting and searching
        columns['id'].set_sort_column_id(0)
        columns['lastName'].set_sort_column_id(2)
        columns['firstName'].set_sort_column_id(1)
        self.allWidgets['tvClientsTable'].set_enable_search(True)
        self.allWidgets['tvClientsTable'].set_search_column(2)
        self.fillClientsTable()

    def fillClientsTable(self):
        """
        Fill clients to the table.
        """
        clients = db.getClients()
        self.clientsListStore.clear()
        for client in clients:
            self.clientsListStore.append([
                    client.db_id,
                    client.first_name,
                    client.last_name,
                    client.address,
                    client.phone,
                    client.mobile_phone1,
                    client.mobile_phone2,
                    client.notes,
                    client.getPreferenceInt('eDistance', 0),
                    ])



    def newClient(self, widget=None):
        """
        Clear input field and set actual_client to None.
        """
        log.debug('newClient()')
        self.actual_client = None
        self.clearClientForm()
        self.fillClientsTable()
        # put cursor to the firstName field
        self.allWidgets['eFirstName'].grab_focus()

    def deleteClient(self, widget):
        """
        Delete actually selected client.
        """
        log.debug('deleteClient(): %s'% repr(self.actual_client))
        if not self.actual_client:
            return
        result = dialogQuestion(text="Opravdu si přejete smazat klienta:",
                secondary_text="%s %s" % (self.actual_client.first_name, 
                    self.actual_client.last_name),
                title="[BeneDat] Dotaz - smazání klienta")
        if gtk.RESPONSE_YES == result:
            db.deleteClient(self.actual_client.db_id)
            self.actual_client = None
            self.clearClientForm()
            self.fillClientsTable()
        # put cursor to the firstName field
        self.allWidgets['eFirstName'].grab_focus()

    def saveClient(self, widget):
        """
        """
        log.debug('saveClient()')
        if not self.allWidgets["eFirstName"].get_text() or \
                not self.allWidgets["eLastName"].get_text():
            log.debug("saveClient: FirstName or LastName not filed. Client didn't saved.")
            return
        if self.actual_client:
            ac = self.actual_client
            # update existing client
            ac.setFirstName(self.allWidgets["eFirstName"].get_text())
            ac.setLastName(self.allWidgets["eLastName"].get_text())
            ac.setAddress(self.allWidgets["eAddress"].get_text())
            ac.setPhone(self.allWidgets["ePhone"].get_text())
            ac.setMobilePhone1(self.allWidgets["eMobilePhone1"].get_text())
            ac.setMobilePhone2(self.allWidgets["eMobilePhone2"].get_text())
            ac.setNotes(self.allWidgets["eNotes"].get_text())
            ac.setPreference("eDistance",self.allWidgets["eDistance"].get_text())
            ac.setPreference("cbDocumentType",self.allWidgets["cbDocumentType"].get_active_text())
            ac.setPreference("chOS", int(self.allWidgets["chOS"].get_active()))
            ac.setPreference("chSTD", int(self.allWidgets["chSTD"].get_active()))
            ac.setPreference("chChB", int(self.allWidgets["chChB"].get_active()))
            # OS
            ac.setPreference("eOSMonthRate", \
                    self.allWidgets["eOSMonthRate"].get_text())
            ac.setPreference("eOSMonthHoursRate", \
                    self.allWidgets["eOSMonthHoursRate"].get_text())
            ac.setPreference("eOSHoursRate1", \
                    self.allWidgets["eOSHoursRate1"].get_text())
            ac.setPreference("eOSHoursRate2", \
                    self.allWidgets["eOSHoursRate2"].get_text())
            ac.setPreference("eOSHoursRate3", \
                    self.allWidgets["eOSHoursRate3"].get_text())
            # ChB
            ac.setPreference("eChBMonthRate", \
                    self.allWidgets["eChBMonthRate"].get_text())
            ac.setPreference("eChBMonthHoursRate", \
                    self.allWidgets["eChBMonthHoursRate"].get_text())
            ac.setPreference("eChBHoursRate1", \
                    self.allWidgets["eChBHoursRate1"].get_text())
            ac.setPreference("eChBHoursRate2", \
                    self.allWidgets["eChBHoursRate2"].get_text())
            ac.setPreference("eChBHoursRate3", \
                    self.allWidgets["eChBHoursRate3"].get_text())
            
            log.info(rnl('Update existing client %s' % repr(self.actual_client)))
            db.updateClient(self.actual_client)
        else:
            # create new client
            self.actual_client = bd_clients.Client(
                    first_name=self.allWidgets["eFirstName"].get_text(),
                    last_name=self.allWidgets["eLastName"].get_text(),
                    address=self.allWidgets["eAddress"].get_text(),
                    phone=self.allWidgets["ePhone"].get_text(),
                    mobile_phone1=self.allWidgets["eMobilePhone1"].get_text(),
                    mobile_phone2=self.allWidgets["eMobilePhone2"].get_text(),
                    notes=self.allWidgets["eNotes"].get_text(),
                    preferences={ \
                        "eDistance":self.allWidgets["eDistance"].get_text(),
                        "cbDocumentType":self.allWidgets["cbDocumentType"].get_active_text(),
                        "chOS":int(self.allWidgets["chOS"].get_active()),
                        "chSTD":int(self.allWidgets["chSTD"].get_active()),
                        "chChB":int(self.allWidgets["chChB"].get_active()),
                        "eOSMonthRate":self.allWidgets["eOSMonthRate"].get_text(),
                        "eOSMonthHoursRate":self.allWidgets["eOSMonthHoursRate"].get_text(),
                        "eOSHoursRate1":self.allWidgets["eOSHoursRate1"].get_text(),
                        "eOSHoursRate2":self.allWidgets["eOSHoursRate2"].get_text(),
                        "eOSHoursRate3":self.allWidgets["eOSHoursRate3"].get_text(),
                        "eChBMonthRate":self.allWidgets["eChBMonthRate"].get_text(),
                        "eChBMonthHoursRate":self.allWidgets["eChBMonthHoursRate"].get_text(),
                        "eChBHoursRate1":self.allWidgets["eChBHoursRate1"].get_text(),
                        "eChBHoursRate2":self.allWidgets["eChBHoursRate2"].get_text(),
                        "eChBHoursRate3":self.allWidgets["eChBHoursRate3"].get_text(),
                        })
            log.info(rnl('Create new client %s' % repr(self.actual_client)))
            #TODO: check if similar client not exist
            db.addClient(self.actual_client)
        self.newClient()
        

    def closeWClients(self, widget):
        """
        """
        log.debug("closeWClients()")
        self.w.destroy()

    def fillClientForm(self, client_id):
        """
        """
        log.debug("fillClientForm(client_id=%s)" % client_id)
        self.actual_client = db.getClient(db_id=client_id)
        log.debug("client: %s" % repr(self.actual_client))
        self.allWidgets["eFirstName"].set_text(self.actual_client.first_name)
        self.allWidgets["eLastName"].set_text(self.actual_client.last_name)
        self.allWidgets["eAddress"].set_text(self.actual_client.address)
        self.allWidgets["ePhone"].set_text(self.actual_client.phone)
        self.allWidgets["eMobilePhone1"].set_text(self.actual_client.mobile_phone1)
        self.allWidgets["eMobilePhone2"].set_text(self.actual_client.mobile_phone2)
        self.allWidgets["eNotes"].set_text(self.actual_client.notes)
        self.allWidgets["eDistance"].set_text("%s" % self.actual_client.getPreferenceInt('eDistance', 0))
        self.fillComboBoxDocumentType(self.actual_client.getPreference('cbDocumentType', "PPD"))
        self.allWidgets["chOS"].set_active(self.actual_client.getPreferenceInt('chOS', 0))
        self.allWidgets["chSTD"].set_active(self.actual_client.getPreferenceInt('chSTD', 0))
        self.allWidgets["chChB"].set_active(self.actual_client.getPreferenceInt('chChB', 0))

        self.allWidgets["eOSMonthRate"].set_text("%s" % \
                self.actual_client.getPreferenceInt('eOSMonthRate', 0))
        self.allWidgets["eOSMonthHoursRate"].set_text("%s" % \
                self.actual_client.getPreferenceInt('eOSMonthHoursRate', 0))
        self.allWidgets["eOSHoursRate1"].set_text("%s" % \
                self.actual_client.getPreferenceInt('eOSHoursRate1', 0))
        self.allWidgets["eOSHoursRate2"].set_text("%s" % \
                self.actual_client.getPreferenceInt('eOSHoursRate2', 0))
        self.allWidgets["eOSHoursRate3"].set_text("%s" % \
                self.actual_client.getPreferenceInt('eOSHoursRate3', 0))
        self.allWidgets["eChBMonthRate"].set_text("%s" % \
                self.actual_client.getPreferenceInt('eChBMonthRate', 0))
        self.allWidgets["eChBMonthHoursRate"].set_text("%s" % \
                self.actual_client.getPreferenceInt('eChBMonthHoursRate', 0))
        self.allWidgets["eChBHoursRate1"].set_text("%s" % \
                self.actual_client.getPreferenceInt('eChBHoursRate1', 0))
        self.allWidgets["eChBHoursRate2"].set_text("%s" % \
                self.actual_client.getPreferenceInt('eChBHoursRate2', 0))
        self.allWidgets["eChBHoursRate3"].set_text("%s" % \
                self.actual_client.getPreferenceInt('eChBHoursRate3', 0))
 


    def clearClientForm(self):
        log.debug("clearClientForm()")
        editable_fields = (
                "eFirstName",
                "eLastName",
                "eAddress",
                "ePhone",
                "eMobilePhone1",
                "eMobilePhone2",
                "eNotes",
                "eDistance",
                "eOSMonthRate",
                "eOSMonthHoursRate",
                "eOSHoursRate1",
                "eOSHoursRate2",
                "eOSHoursRate3",
                "eChBMonthRate",
                "eChBMonthHoursRate",
                "eChBHoursRate1",
                "eChBHoursRate2",
                "eChBHoursRate3",
                )
        for e in editable_fields:
            self.allWidgets[e].set_text('')
        
        ch_fields = (
                "chOS",
                "chSTD",
                "chChB",
                )
        for e in ch_fields:
            self.allWidgets[e].set_active(False)
        
        self.fillComboBoxDocumentType()

    def cursorChanged(self, selected):
        log.debug("cursorChanged(%s)" % selected)
        (model,iter) = selected.get_selected()
        if iter:
            client_id = self.clientsListStore.get_value(iter, 0)
            self.fillClientForm(client_id)

    def chOStoggled(self, widget):
        log.debug("chOStoggled()")
        self.allWidgets['exOS'].set_expanded( \
                self.allWidgets['chOS'].get_active())

    def chChBtoggled(self, widget):
        log.debug("chChBtoggled")
        self.allWidgets['exChB'].set_expanded( \
                self.allWidgets['chChB'].get_active())

    def nothing(self, widget, parameters=None):
        log.debug("Do nothing (parameters: %s)"%parameters)


class WRecords():
    """
    BeneDat records window
    """
    def __init__(self):
        # Actual record
        self.actual_record = None

        # "actual" date
        self.actual_date = bd_datetime.Date()

        # widgets for services
        self.services = {}
        self.time_records_to_remove = []

        # Window
        self.wxml = gtk.glade.XML(GLADEFILE, "wRecords")
        self.w = self.wxml.get_widget("wRecords")

        # Signals
        signals = {
                "on_wRecords_btNewRecord_clicked": self.newRecord,
                "on_wRecords_btDeleteRecord_clicked": self.deleteRecord,
                "on_wRecords_btClose_clicked": self.closeWRecords,
                "on_wRecords_destroy": self.closeWRecords,
                "on_wRecords_tbtFilter_toggled": self.filterChanged,
                "on_wRecords_cbFilterMonth_changed": self.filterChanged,
                "on_wRecords_cbFilterYear_changed": self.filterChanged,
                "on_wRecords_btClient_clicked": self.clientsMenu,
                "on_wRecords_btDate_clicked": self.calendarWindow,
                "on_wRecords_btAddService_clicked": self.addService,
                "on_wRecords_btSaveRecord_clicked": self.saveRecord,
                "on_wRecords_eDate_focus_out_event": self.eDate_focus_out_event,
                "on_wRecords_eDate_key_release_event":self.eDate_key_release,
                "on_wRecords_expTravel_activate":self.expTravel_activate,
                "on_wRecords_expDiet_activate":self.expDiet_activate,
                "on_wRecords_expBillet_activate":self.expBillet_activate,
                }
        self.wxml.signal_autoconnect(signals)

        # Widgets
        self.allWidgets = {}
        widgets = (
                'tbtFilter',
                'cbFilterMonth',
                'cbFilterYear',
                'tvRecordsTable',
                'eClient',
                'eDate',
                'tabServices',
                'btAddService',
                'eTransportServiceOther',
                'eDietOther',
                'eBilletOther',
                'chTransportOnService',
                'chTransportFromService',
                'chTransportChMo',
                'chTransportMoCh',
                'chDietRefreshmentCh',
                'chDietRefreshmentM',
                'chDietLunchCh',
                'chDietLunchM',
                'chDietBreakfastM',
                'chDietDinnerM',
                'chBilletChB1',
                'chBilletChB2',
                'chBilletChB3',
                'chBilletOS',
                'expTravel',
                'expDiet',
                'expBillet',
                )
        for widget in widgets:
            self.allWidgets[widget] = self.wxml.get_widget("wRecords_%s"%widget)

        self.recordsListStore = None

        # prepare filter
        self.loadFilter()

        # connect signal for select row by simple click
        self.allWidgets['tvRecordsTable'].get_selection().connect('changed',self.cursorChanged)
        # sort records table by date
        self.recordsListStore.set_sort_column_id(1, gtk.SORT_ASCENDING)
        self.recordsListStore.set_sort_column_id(23, gtk.SORT_ASCENDING)

        # create clients menu
        self.createClientsMenu()

        # setup completion
        self.clientEntryCompletion()

        # add one "line" for services
        self.addService(widget=None)

        # put cursor to the eClient field
        self.allWidgets['eClient'].grab_focus()

    def run(self):
        log.debug("<WRecords>.w.show_all()"%self)
        self.w.show_all()

    def fillComboBoxFilterMonth(self, month=''):
        """
        Fill combo box for filter (month).
        """
        log.debug("fillComboBoxFilterMonth")
        monthListStore = gtk.ListStore(str, str)
        self.allWidgets['cbFilterMonth'].set_model(monthListStore)
        cell = gtk.CellRendererText()
        self.allWidgets['cbFilterMonth'].pack_start(cell, True)
        self.allWidgets['cbFilterMonth'].add_attribute(cell, 'text', 1)
        monthListStore.clear()
        months =  {
                ''  : '',
                '01': 'Leden',
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
        mkeys = months.keys()
        mkeys.sort()
        for month_ in mkeys:
            monthListStore.append([month_, months[month_]])
        if month:
            i = 0
            for m in monthListStore:
                if m[0] == month:
                    break
                else:
                    i+=1
            self.allWidgets['cbFilterMonth'].set_active(i)

    def fillComboBoxFilterYear(self, year=None):
        """
        Fill combo box for filter (year).
        """
        log.debug("fillComboBoxFilterYear")
        yearListStore = gtk.ListStore(str)
        self.allWidgets['cbFilterYear'].set_model(yearListStore)
        cell = gtk.CellRendererText()
        self.allWidgets['cbFilterYear'].pack_start(cell, True)
        self.allWidgets['cbFilterYear'].add_attribute(cell, 'text', 0)
        yearListStore.clear()
        years = db.getRecordsYears()
        this_year = "%s" % bd_datetime.Date().date.year
        if not this_year in years:
            years.append(this_year)
        years.sort()
        for year_ in years:
            yearListStore.append([year_])
        if year:
            i = 0
            for y in yearListStore:
                if y[0] == year:
                    break
                else:
                    i+=1
            self.allWidgets['cbFilterYear'].set_active(i)



    def prepareRecordsTable(self):
        """
        Prepare and fill table of records.
        """
        log.debug("prepareRecordsTable()")
        self.recordsListStore = gtk.ListStore(
                int, # 0 id
                str, # 1 client (LastName FirstName)
                str, # 2 date
                str, # 3 service_type
                str, # 4 time_from
                str, # 5 time_to
                #
                gobject.TYPE_BOOLEAN,   #  6 TOS       chTransportOnService
                gobject.TYPE_BOOLEAN,   #  7 TFS       chTransportFromService
                gobject.TYPE_BOOLEAN,   #  8 TChMo     chTransportChMo
                gobject.TYPE_BOOLEAN,   #  9 TMoCh     chTransportMoCh
                str,                    # 10 TSO       eTransportServiceOther
                gobject.TYPE_BOOLEAN,   # 11 DRCh      chDietRefreshmentCh
                gobject.TYPE_BOOLEAN,   # 12 DRM       chDietRefreshmentM
                gobject.TYPE_BOOLEAN,   # 13 DLCh      chDietLunchCh
                gobject.TYPE_BOOLEAN,   # 14 DLM       chDietLunchM
                gobject.TYPE_BOOLEAN,   # 15 DBM       chDietBreakfastM
                gobject.TYPE_BOOLEAN,   # 16 DDM       chDietDinnerM
                str,                    # 17 DO        eDietOther
                gobject.TYPE_BOOLEAN,   # 18 BChB1     chBilletChB1
                gobject.TYPE_BOOLEAN,   # 19 BChB2     chBilletChB2
                gobject.TYPE_BOOLEAN,   # 20 BChB3     chBilletChB3
                gobject.TYPE_BOOLEAN,   # 21 BOS       chBilletOS
                str,                    # 22 BO        eBilletOther
                #
                str, # 23 date for sorting
                )
        self.allWidgets['tvRecordsTable'].set_model(self.recordsListStore)

        columns = {}
        crt = gtk.CellRendererText()
        crt.set_alignment(0.0,0.0)
        columns['name'] = gtk.TreeViewColumn("Jméno",
                crt,
                text=1)
        crt = gtk.CellRendererText()
        crt.set_alignment(1.0,0.0)
        columns['date'] = gtk.TreeViewColumn("Datum",
                crt,
                text=2)
        crt = gtk.CellRendererText()
        crt.set_alignment(0.5,0.0)
        columns['service_type'] = gtk.TreeViewColumn("Služba",
                crt,
                text=3)
        crt = gtk.CellRendererText()
        crt.set_alignment(1.0,0.0)
        columns['time_from'] = gtk.TreeViewColumn("Čas od",
                crt,
                text=4)
        crt = gtk.CellRendererText()
        crt.set_alignment(1.0,0.0)
        columns['time_to'] = gtk.TreeViewColumn("Čas do",
                crt,
                text=5)
        #
        crt = gtk.CellRendererToggle()
        crt.set_alignment(0.5,0.0)
        columns['TOS'] = gtk.TreeViewColumn("Doprava\nna službu",
                crt,
                active=6)
        crt = gtk.CellRendererToggle()
        crt.set_alignment(0.5,0.0)
        columns['TFS'] = gtk.TreeViewColumn("Doprava\nze služby",
                crt,
                active=7)
        crt = gtk.CellRendererToggle()
        crt.set_alignment(0.5,0.0)
        columns['TChMo'] = gtk.TreeViewColumn("Doprava\nCh>Mo",
                crt,
                active=8)
        crt = gtk.CellRendererToggle()
        crt.set_alignment(0.5,0.0)
        columns['TMoCh'] = gtk.TreeViewColumn("Doprava\nMo>Ch",
                crt,
                active=9)
        crt = gtk.CellRendererText()
        crt.set_alignment(1.0,0.0)
        columns['TSO'] = gtk.TreeViewColumn("Doprava\nostatní",
                crt,
                text=10)

        crt = gtk.CellRendererToggle()
        crt.set_alignment(0.5,0.0)
        columns['DRCh'] = gtk.TreeViewColumn("Občerstvení\nChotěboř",
                crt,
                active=11)
        crt = gtk.CellRendererToggle()
        crt.set_alignment(0.5,0.0)
        columns['DRM'] = gtk.TreeViewColumn("Občerstvení\nModletín",
                crt,
                active=12)
        crt = gtk.CellRendererToggle()
        crt.set_alignment(0.5,0.0)
        columns['DLCh'] = gtk.TreeViewColumn("Oběd\nChotěboř",
                crt,
                active=13)
        crt = gtk.CellRendererToggle()
        crt.set_alignment(0.5,0.0)
        columns['DLM'] = gtk.TreeViewColumn("Oběd\nModletín",
                crt,
                active=14)
        crt = gtk.CellRendererToggle()
        crt.set_alignment(0.5,0.0)
        columns['DBM'] = gtk.TreeViewColumn("Snídaně\nModletín",
                crt,
                active=15)
        crt = gtk.CellRendererToggle()
        crt.set_alignment(0.5,0.0)
        columns['DDM'] = gtk.TreeViewColumn("Večeře\nModletín",
                crt,
                active=16)
        crt = gtk.CellRendererText()
        crt.set_alignment(1.0,0.0)
        columns['DO'] = gtk.TreeViewColumn("Jídlo\nostatní",
                crt,
                text=17)

        crt = gtk.CellRendererToggle()
        crt.set_alignment(0.5,0.0)
        columns['BChB1'] = gtk.TreeViewColumn("Chráněné\nbydlení 1",
                crt,
                active=18)
        crt = gtk.CellRendererToggle()
        crt.set_alignment(0.5,0.0)
        columns['BChB2'] = gtk.TreeViewColumn("Chráněné\nbydlení 2",
                crt,
                active=19)
        crt = gtk.CellRendererToggle()
        crt.set_alignment(0.5,0.0)
        columns['BChB3'] = gtk.TreeViewColumn("Chráněné\nbydlení 2",
                crt,
                active=20)
        crt = gtk.CellRendererToggle()
        crt.set_alignment(0.5,0.0)
        columns['BOS'] = gtk.TreeViewColumn("Ubytování\nOS",
                crt,
                active=21)
        crt = gtk.CellRendererText()
        crt.set_alignment(1.0,0.0)
        columns['BO'] = gtk.TreeViewColumn("Ubytování\nostatní",
                crt,
                text=22)
        # empty space (because of expanding)
        columns['space'] = gtk.TreeViewColumn("",
            gtk.CellRendererText())

        columns_order = (
                'name',
                'date',
                'service_type',
                'time_from',
                'time_to',
                'TOS',
                'TFS',
                'TChMo',
                'TMoCh',
                'TSO',
                'DRCh',
                'DRM',
                'DLCh',
                'DLM',
                'DBM',
                'DDM',
                'DO',
                'BChB1',
                'BChB2',
                'BChB3',
                'BOS',
                'BO',
                'space'
                )
        for column in columns_order:
            self.allWidgets['tvRecordsTable'].append_column(columns[column])

        # configure sorting and searching
        columns['date'].set_sort_column_id(23)
        columns['name'].set_sort_column_id(1)
        self.allWidgets['tvRecordsTable'].set_enable_search(True)
        self.allWidgets['tvRecordsTable'].set_search_column(1)
        self.fillRecordsTable()

    def fillRecordsTable(self):
        """
        Fill records to the table.
        """
        log.debug("fillRecordsTable()")
        if self.recordsListStore is None:
            # prepare and fill table of records
            self.prepareRecordsTable()

        if self.allWidgets['tbtFilter'].get_active():
            records = db.getRecords( \
                    year=self.allWidgets['cbFilterYear'].get_active_text(), \
                    month=self.allWidgets['cbFilterMonth'].get_active_text())
        else:
            records = db.getRecords()

        self.recordsListStore.clear()
        for record in records:
            # prepare time records
            time_records = {
                    'service_type': '',
                    'time_from': '',
                    'time_to': ''}
            for tr in record.time_records:
                time_records['service_type'] += "%s\n" % tr.service_type
                time_records['time_from'] += "%s\n" % tr.time_from
                time_records['time_to'] += "%s\n" % tr.time_to
            # prepare value records
            def x(val):
                return "x" if val else "-"
            vrs = record.value_records
            # fill records
            self.recordsListStore.append([
                    record.db_id,           #  0
                    "%s %s" % (record.client.last_name, record.client.first_name),
                    "%s" % record.date,     #  2
                    time_records['service_type'].strip(),   # 3
                    time_records['time_from'].strip(),      # 4
                    time_records['time_to'].strip(),        # 5
                    vrs['TOS'].value,       #  6
                    vrs['TFS'].value,       #  7
                    vrs['TChMo'].value,     #  8
                    vrs['TMoCh'].value,     #  9
                    vrs['TSO'].value,       # 10
                    vrs['DRCh'].value,      # 11
                    vrs['DRM'].value,       # 12
                    vrs['DLCh'].value,      # 13
                    vrs['DLM'].value,       # 14
                    vrs['DBM'].value,       # 15
                    vrs['DDM'].value,       # 16
                    vrs['DO'].value,        # 17
                    vrs['BChB1'].value,     # 18
                    vrs['BChB2'].value,     # 19
                    vrs['BChB3'].value,     # 20
                    vrs['BOS'].value,       # 21
                    vrs['BO'].value,        # 22
                    "%s" % record.date.get('yyyy-mm-dd'),   # 23
                    ])
        

    def closeWRecords(self, widget):
        """
        """
        log.debug("closeWRecords()")
        self.w.destroy()


    def newRecord(self, widget=None):
        """
        Clear input field and set actual_record to None.
        """
        log.debug("newRecord()")
        self.actual_record = None
        self.clearRecordForm()
        # put cursor to the eClient field
        self.allWidgets['eClient'].grab_focus()

    def deleteRecord(self, widget):
        """
        Delete actually selected record.
        """
        log.debug("deleteRecord(): %s" % repr(self.actual_record))
        if not self.actual_record:
            return
        result = dialogQuestion(text="Opravdu si přejete smazat záznam:",
                secondary_text="%s %s" % (self.actual_record.client.first_name, 
                    self.actual_record.client.last_name),
                title="[BeneDat] Dotaz - smazání záznamu")
        if gtk.RESPONSE_YES == result:
            db.deleteRecord(self.actual_record.db_id)
            self.actual_record = None
            self.clearRecordForm()
            self.fillRecordsTable()
        self.allWidgets['eClient'].grab_focus()


    def saveRecord(self, widget):
        """
        Save selected/created record.
        """
        log.debug("saveRecord(): actual_record=%s" % repr(self.actual_record))
        # check filled fields
        client = db.getClient(name=self.allWidgets['eClient'].get_text())
        if not client:
            return
        date = Date(self.allWidgets['eDate'].get_text())
        if db.getRecords(client=client.db_id, date=date.get(format_='yyyy-mm-dd')):
            result = dialogQuestion(text="Záznam s datem '%s' pro klienta '%s %s' již existuje.\n"
                    "Přejete si přesto přidat tento záznam?" % \
                    (date.get(), client.first_name, client.last_name), \
                    title='[BeneDat] Dotaz - podobný záznam')
            if gtk.RESPONSE_YES != result:
                return

        # TODO: check filled fields - is it necessary?
        
        # update existing or add new record
        if self.actual_record:
            # update existing record
            self.actual_record.setClient(client)
            self.actual_record.setDate(self.allWidgets['eDate'].get_text())
        else:
            # create (add) new record
            self.actual_record = bd_records.Record(
                    client = client,
                    date = self.allWidgets['eDate'].get_text())
        
        # insert time records
        for key in self.services:
            if self.services[key]['db_id']:
                self.actual_record.updateTimeRecord(
                        service_type=self.services[key]['type']. \
                                get_active_text(),
                        time_from=self.services[key]['from'].get_text(),
                        time_to=self.services[key]['to'].get_text(),
                        db_id=self.services[key]['db_id'])
            else:
                self.actual_record.addTimeRecord(
                        service_type=self.services[key]['type']. \
                                get_active_text(),
                        time_from=self.services[key]['from'].get_text(),
                        time_to=self.services[key]['to'].get_text())

        # remove removed time_record
        for tr in self.time_records_to_remove:
            db.deleteTimeRecord(db_id=tr)
        self.time_records_to_remove = []

        
        # insert/update value records
        self.actual_record.addValueRecord(
                service_type="TSO", 
                value=self.allWidgets["eTransportServiceOther"].get_text())
        self.actual_record.addValueRecord(
                service_type="DO", 
                value=self.allWidgets["eDietOther"].get_text())
        self.actual_record.addValueRecord(
                service_type="BO", 
                value=self.allWidgets["eBilletOther"].get_text())
        self.actual_record.addValueRecord(
                service_type="TOS", 
                value=self.allWidgets["chTransportOnService"].get_active())
        self.actual_record.addValueRecord(
                service_type="TFS", 
                value=self.allWidgets["chTransportFromService"].get_active())
        self.actual_record.addValueRecord(
                service_type="TChMo", 
                value=self.allWidgets["chTransportChMo"].get_active())
        self.actual_record.addValueRecord(
                service_type="TMoCh", 
                value=self.allWidgets["chTransportMoCh"].get_active())
        self.actual_record.addValueRecord(
                service_type="DRCh", 
                value=self.allWidgets["chDietRefreshmentCh"].get_active())
        self.actual_record.addValueRecord(
                service_type="DRM", 
                value=self.allWidgets["chDietRefreshmentM"].get_active())
        self.actual_record.addValueRecord(
                service_type="DLCh", 
                value=self.allWidgets["chDietLunchCh"].get_active())
        self.actual_record.addValueRecord(
                service_type="DLM", 
                value=self.allWidgets["chDietLunchM"].get_active())
        self.actual_record.addValueRecord(
                service_type="DBM", 
                value=self.allWidgets["chDietBreakfastM"].get_active())
        self.actual_record.addValueRecord(
                service_type="DDM", 
                value=self.allWidgets["chDietDinnerM"].get_active())
        self.actual_record.addValueRecord(
                service_type="BChB1", 
                value=self.allWidgets["chBilletChB1"].get_active())
        self.actual_record.addValueRecord(
                service_type="BChB2", 
                value=self.allWidgets["chBilletChB2"].get_active())
        self.actual_record.addValueRecord(
                service_type="BChB3", 
                value=self.allWidgets["chBilletChB3"].get_active())
        self.actual_record.addValueRecord(
                service_type="BOS", 
                value=self.allWidgets["chBilletOS"].get_active())

        if self.actual_record.db_id:
            # update existing record
            log.info(rnl('Update record %s' % repr(self.actual_record)))
            db.updateRecord(self.actual_record)
        else:
            # create (add) new record
            log.info(rnl('Create new record %s' % repr(self.actual_record)))
            db.addRecord(self.actual_record)

        self.fillRecordsTable()
        # clear input fields (form)
        self.newRecord()


    def createClientsMenu(self):
        """
        Prepare pop up menu with clients.
        """
        self.MenuClients = gtk.Menu()

        clients = db.getClients()

        c_item = {}
        for client in clients:
            c = "%s %s" % (client.last_name, client.first_name)
            c_item[c] = gtk.MenuItem("%s %s" % \
                    (client.last_name, client.first_name))
            c_item[c].connect_object("activate", self.clientsMenuClicked, c)
            self.MenuClients.append(c_item[c])

        self.MenuClients.show_all()

    def clientsMenu(self, widget):
        """
        Popup menu with list of clients.
        """
        self.MenuClients.popup(None, None, None, 0, 0)

    def clientsMenuClicked(self, data):
        """
        Serve clients menu clicked.
        """
        log.debug("clientsMenuClicked('%s')"%data)
        self.allWidgets['eClient'].set_text(data)
        self.allWidgets['eDate'].grab_focus()


    def clientEntryCompletion(self):
        """
        Set up entry completion for client field.
        """
        completion = gtk.EntryCompletion()

        self.clientsListStore = gtk.ListStore(
                str, # Full Name
                )
        clients = db.getClients()
        for client in clients:
            # FirstName LastName
            self.clientsListStore.append([
                    "%s %s" % (client.last_name, client.first_name)
                    ])
            # LastName FirstName
            self.clientsListStore.append([
                    "%s %s" % (client.first_name, client.last_name)
                    ])

        completion.set_model(self.clientsListStore)
        self.allWidgets['eClient'].set_completion(completion)
        completion.set_text_column(0)
        completion.set_minimum_key_length(0)

    def calendarWindow(self, widget):
        """
        Open window with calendar.
        """
        log.debug("calendarWindow()")
        date = dialogCalendar(self.w)
        if date:
            self.allWidgets['eDate'].set_text(date)

    def eDate_key_release(self, widget, parameters):
        """
        """
        if parameters.string in ('+', '-'):
            log.debug("eDate_key_release('%s')" % parameters.string)
            #widget.set_text(widget.get_text().replace('-','').replace('+',''))
            self.actual_date.set(parameters.string)
            self.allWidgets['eDate'].set_text(self.actual_date.get())

    def eDate_focus_out_event(self, widget, parameters):
        """
        """
        log.debug("WRecords.eDate_focus_out_event()")
        self.actual_date.set(self.allWidgets['eDate'].get_text())

        self.allWidgets['eDate'].set_text(self.actual_date.get())

    def eFromTo_focus_out_event(self, widget, parameters):
        """
        """
        log.debug("WRecords.eFromTo_focus_out_event()")
        d = Time(widget.get_text())
        widget.set_text(d.get())

    def fillComboBoxService(self, cbwidget):
        """
        Fill combo box field for services (OS, STD, ChB)
        """
        servicesListStore = gtk.ListStore(str)
        cbwidget.set_model(servicesListStore)
        cell = gtk.CellRendererText()
        cbwidget.pack_start(cell, True)
        cbwidget.add_attribute(cell, 'text', 0)

        servicesListStore.clear()
        services = ('OS', 'STD', 'ChB')
        for service in services:
            servicesListStore.append([service])
        cbwidget.set_active(0)



    def addService(self, widget, time_record=None):
        """
        Add widget for service ... (and fill time_record if present)
        """
        if self.services:
            last_max_id = max(self.services.keys())
            id_ = last_max_id + 1
        else:
            last_max_id = None
            id_ = 0
        log.debug("Adding widgets for service (id=%s)."%id_)
        top_attach = id_+1
        bottom_attach = id_+2
        service = {}
        # service type
        service['type'] = gtk.ComboBox()
        self.fillComboBoxService(service['type'])
        # add widget to the window
        self.allWidgets['tabServices'].attach(service['type'], \
                0,1,top_attach, bottom_attach, \
                xoptions=gtk.FILL, yoptions=gtk.FILL)
        # from time 
        service['from'] = gtk.Entry()
        service['from'].set_width_chars(5)
        service['from'].set_max_length(5)
        service['from'].set_activates_default(True)
        service['from'].connect('focus-out-event', self.eFromTo_focus_out_event)
        # fill 'to' time from previous line
        if last_max_id is not None:
            service['from'].set_text(self.services[last_max_id]['to'].get_text())
        # add widget to the window
        self.allWidgets['tabServices'].attach(service['from'], \
                1,2,top_attach, bottom_attach, \
                xoptions=gtk.FILL, yoptions=gtk.FILL)
        # to time
        service['to'] = gtk.Entry()
        service['to'].set_width_chars(5)
        service['to'].set_max_length(5)
        service['to'].set_activates_default(True)
        service['to'].connect('focus-out-event', self.eFromTo_focus_out_event)
        # add widget to the window
        self.allWidgets['tabServices'].attach(service['to'], \
                2,3,top_attach, bottom_attach, \
                xoptions=gtk.FILL, yoptions=gtk.FILL)
        # remove button
        service['remove'] = gtk.Button(label=" - ")
        service['remove'].connect('clicked', self.deleteService, id_, True)
        # add widget to the window
        self.allWidgets['tabServices'].attach(service['remove'], \
                3,4,top_attach, bottom_attach, \
                xoptions=gtk.FILL, yoptions=gtk.FILL)
        # show all widgets
        self.allWidgets['tabServices'].show_all()
        # put cursor to the first added field
        service['type'].grab_focus()
        service['db_id'] = 0
        
        # Fill time_record to prepared field 
        if time_record: 
            log.debug("Fill time_record to prepared fields (time_record=%s)." % \
                    time_record)
            # select service type
            i = 0
            for type_ in service['type'].get_model():
                if type_[0] == time_record.getServiceType():
                    break
                else:
                    i+=1
            service['type'].set_active(i)
            #
            service['from'].set_text(time_record.time_from.get())
            service['to'].set_text(time_record.time_to.get())
            service['db_id'] = time_record.db_id

        # add service between all services
        self.services[id_]= service

    def deleteService(self, widget, id_, from_db=False):
        """
        Delete widgets for service ...
        """
        log.debug("Removing widgets for service (id=%s)."%id_)
        if from_db:
            if self.services[id_]['db_id']:
                self.time_records_to_remove.append(self.services[id_]['db_id'])
        self.allWidgets['tabServices'].remove(self.services[id_]['type'])
        self.allWidgets['tabServices'].remove(self.services[id_]['from'])
        self.allWidgets['tabServices'].remove(self.services[id_]['to'])
        self.allWidgets['tabServices'].remove(self.services[id_]['remove'])
        self.allWidgets['btAddService'].grab_focus()
        del self.services[id_]

    def deleteAllServices(self):
        """
        Delete all filed for time_records.
        """
        for key in self.services.keys():
            self.deleteService(widget=None, id_=key)

    def cursorChanged(self, selected):
        log.debug("cursorChanged(%s)" % selected)
        (model,iter) = selected.get_selected()
        if iter:
            record_id = self.recordsListStore.get_value(iter, 0)
            self.fillRecordForm(record_id)
    
    def fillRecordForm(self, record_id):
        """
        """
        log.debug("fillRecordForm(record_id=%s)" % record_id)
        self.actual_record = db.getRecord(db_id=record_id)
        log.debug("record: %s" % self.actual_record)
        # fill client name
        self.allWidgets['eClient'].set_text(
                "%s %s" % (self.actual_record.client.last_name, \
                        self.actual_record.client.first_name))
        # fill date
        self.allWidgets['eDate'].set_text(self.actual_record.date.get())
        self.actual_date.set(self.actual_record.date.get())
        # fill time records
        self.deleteAllServices()
        for time_record in self.actual_record.time_records:
            self.addService(widget=None, time_record=time_record)
        # fill value records
        self.allWidgets["eTransportServiceOther"].set_text(
                str(self.actual_record.value_records["TSO"].value))
        self.allWidgets["eDietOther"].set_text(
                str(self.actual_record.value_records["DO"].value))
        self.allWidgets["eBilletOther"].set_text(
                str(self.actual_record.value_records["BO"].value))
        self.allWidgets["chTransportOnService"].set_active(
                self.actual_record.value_records["TOS"].value)
        self.allWidgets["chTransportFromService"].set_active(
                self.actual_record.value_records["TFS"].value)
        self.allWidgets["chTransportChMo"].set_active(
                self.actual_record.value_records["TChMo"].value)
        self.allWidgets["chTransportMoCh"].set_active(
                self.actual_record.value_records["TMoCh"].value)
        self.allWidgets["chDietRefreshmentCh"].set_active(
                self.actual_record.value_records["DRCh"].value)
        self.allWidgets["chDietRefreshmentM"].set_active(
                self.actual_record.value_records["DRM"].value)
        self.allWidgets["chDietLunchCh"].set_active(
                self.actual_record.value_records["DLCh"].value)
        self.allWidgets["chDietLunchM"].set_active(
                self.actual_record.value_records["DLM"].value)
        self.allWidgets["chDietBreakfastM"].set_active(
                self.actual_record.value_records["DBM"].value)
        self.allWidgets["chDietDinnerM"].set_active(
                self.actual_record.value_records["DDM"].value)
        self.allWidgets["chBilletChB1"].set_active(
                self.actual_record.value_records["BChB1"].value)
        self.allWidgets["chBilletChB2"].set_active(
                self.actual_record.value_records["BChB2"].value)
        self.allWidgets["chBilletChB3"].set_active(
                self.actual_record.value_records["BChB3"].value)
        self.allWidgets["chBilletOS"].set_active(
                self.actual_record.value_records["BOS"].value)

    def clearRecordForm(self):
        log.debug("clearRecordForm()")
        editable_fields = (
                "eClient",
                "eDate",
                'eTransportServiceOther',
                'eDietOther',
                'eBilletOther',
                )
        for e in editable_fields:
            self.allWidgets[e].set_text('')
        fields = (
                'chTransportOnService',
                'chTransportFromService',
                'chTransportChMo',
                'chTransportMoCh',
                'chDietRefreshmentCh',
                'chDietRefreshmentM',
                'chDietLunchCh',
                'chDietLunchM',
                'chDietBreakfastM',
                'chDietDinnerM',
                'chBilletChB1',
                'chBilletChB2',
                'chBilletChB3',
                'chBilletOS',
                )
        for e in fields:
            self.allWidgets[e].set_active(False)

        # remove all time record fields
        self.deleteAllServices()
        #
        self.addService(widget=None)
        self.fillRecordsTable()

    def expTravel_activate(self, widget):
        self.allWidgets['expDiet'].set_expanded(False)
        self.allWidgets['expBillet'].set_expanded(False)
    def expDiet_activate(self, widget):
        self.allWidgets['expTravel'].set_expanded(False)
        self.allWidgets['expBillet'].set_expanded(False)
    def expBillet_activate(self, widget):
        self.allWidgets['expDiet'].set_expanded(False)
        self.allWidgets['expTravel'].set_expanded(False)


    def filterChanged(self, widget=None):
        """
        Reload records table when filter is changed.
        """
        log.debug("filterChanged()")
        self.fillRecordsTable()
        self.saveFilter()

    def saveFilter(self):
        """
        Save filter settings.
        """
        log.debug("saveFilter()")
        db.setConf("WRecords_tbtFilter", \
                int(self.allWidgets['tbtFilter'].get_active()), \
                "Filter v okně záznamů.", commit=False)
        if self.allWidgets['cbFilterYear'].get_model():
            db.setConf("WRecords_cbFilterYear", \
                    self.allWidgets['cbFilterYear'].get_active_text(), \
                    "Filter v okně záznamů - rok.", commit=False)
        if self.allWidgets['cbFilterMonth'].get_model():
            db.setConf("WRecords_cbFilterMonth", \
                    self.allWidgets['cbFilterMonth'].get_active_text(), \
                    "Filter v okně záznamů - měsíc.", commit=False)

    def loadFilter(self):
        """
        Load filter settings.
        """
        log.debug("loadFilter()")
        # block signal handler when changing filter
        self.allWidgets['cbFilterYear'].handler_block_by_func(self.filterChanged)
        self.allWidgets['cbFilterMonth'].handler_block_by_func(self.filterChanged)
        # load filter
        self.allWidgets['tbtFilter'].set_active( \
                bool(int(db.getConfVal('WRecords_tbtFilter', 1))))
        this_year = "%s" % bd_datetime.Date().date.year
        self.fillComboBoxFilterYear( \
                db.getConfVal('WRecords_cbFilterYear', this_year))
        self.fillComboBoxFilterMonth( \
                db.getConfVal('WRecords_cbFilterMonth', ''))
        # unblock signal handler when changing filter
        self.allWidgets['cbFilterYear'].handler_unblock_by_func(self.filterChanged)
        self.allWidgets['cbFilterMonth'].handler_unblock_by_func(self.filterChanged)
        self.filterChanged()


    def nothing(self, widget, parameters=None):
        log.debug("Do nothing (parameters: %s)"%parameters)



class WSummary():
    """
    BeneDat summary window.
    """
    def __init__(self):
        # Window
        self.wxml = gtk.glade.XML(GLADEFILE, "wSummary")
        self.w = self.wxml.get_widget("wSummary")
        
        # Signals
        signals = {
                "": self.nothing,
                "on_wSummary_destroy": self.nothing,
                "on_wSummary_cbFilterMonth_changed": self.filterChangedMonth,
                "on_wSummary_cbFilterYear_changed": self.filterChangedYear,
                "on_wSummary_btFilterToday_clicked": self.filterToday,
                "on_wSummary_cbDocumentType_changed": self.cbDocumentType_changed,
                "on_wSummary_btDateIssue_clicked": self.calendarWindowIssue,
                "on_wSummary_btDatePayment_clicked": self.calendarWindowPayment,
                "on_wSummary_btClose_clicked": self.closeWSummary,
                "on_wSummary_btSave_clicked": self.saveSummary,
                }
        self.wxml.signal_autoconnect(signals)

        # Widgets 
        self.allWidgets = {}
        widgets = (
                "cbFilterMonth",
                "cbFilterYear",
                "btFilterToday",
                "cbDocumentType",
                "tvClientsTable",
                "btDateIssue",
                "eDateIssue",
                "btDatePayment",
                "eDatePayment",
                "eClerkName",
                "eCodeFixed",
                "eCodeVariable",
                "btClose",
                "btSave",
                )
        for widget in widgets:
            self.allWidgets[widget] = self.wxml.get_widget("wSummary_%s"%widget)

        # prepare document type combobox
        self.prepareComboBoxDocumentType()

        # prepare filter
        self.prepareFilter()
        # prepare clients table
        self.prepareClientsTable()
        # load filter
        self.loadFilter()

        # fill date fields
        self.allWidgets['eDateIssue'].set_text(bd_datetime.Date().get())
        self.allWidgets['eDatePayment'].set_text(bd_datetime.Date().get())

        # fill clerk_name
        self.allWidgets['eClerkName'].set_text( \
                db.getConfVal("wSummary_eClerkName", ""))
        
        # fill summary code
        self.allWidgets['eCodeFixed'].set_text( \
                db.getConfVal("eSummaryCodeFixed", "XXXX"))
        self.allWidgets['eCodeVariable'].set_text( \
                db.getConfVal("eSummaryCodeVariable", "0001"))

        # list of selected clients
        self.clients = []

    def run(self):
        log.debug("<wSummary>.w.show_all()")
        self.w.show_all()


    def closeWSummary(self, widget):
        """
        """
        log.debug("closeWSummary()")
        self.w.destroy()

    def filterToday(self, widget):
        """
        Set filter to "today".
        """
        log.debug("filterToday()")
        this_year = "%s" % bd_datetime.Date().date.year
        self.fillComboBoxFilterYear(this_year)
        this_month = "%02d" % bd_datetime.Date().date.month
        self.fillComboBoxFilterMonth(this_month)

    def filterChanged(self):
        """
        Reload clients table when filter is changed.
        """
        log.debug("filterChanged()")
        self.fillClientsTable()

    def filterChangedYear(self, widget):
        self.saveFilterYear()
        self.filterChanged()

    def filterChangedMonth(self, widget):
        self.saveFilterMonth()
        self.filterChanged()

    def prepareFilter(self):
        self.prepareComboBoxFilterYear()
        self.prepareComboBoxFilterMonth()


    def loadFilter(self):
        """
        Load filter.
        """
        log.debug("loadFilter()")
        # load filter
        this_year = "%s" % bd_datetime.Date().date.year
        self.fillComboBoxFilterYear( \
                db.getConfVal('WSummary_cbFilterYear', this_year))
        this_month = "%02d" % bd_datetime.Date().date.month
        self.fillComboBoxFilterMonth( \
                db.getConfVal('WSummary_cbFilterMonth', this_month))

    def saveFilterYear(self):
        """
        Save year filter settings.
        """
        log.debug("saveFilterYear()")
        if self.allWidgets['cbFilterYear'].get_model():
            db.setConf("WSummary_cbFilterYear", \
                    self.allWidgets['cbFilterYear'].get_active_text(), \
                    "Filter v okně sestav - rok.", commit=False)

    def saveFilterMonth(self):
        """
        Save month filter settings.
        """
        log.debug("saveFilterMonth()")
        if self.allWidgets['cbFilterMonth'].get_model():
            db.setConf("WSummary_cbFilterMonth", \
                    self.allWidgets['cbFilterMonth'].get_active_text(), \
                    "Filter v okně sestav - měsíc.", commit=False)

    def prepareComboBoxFilterYear(self):
        self.yearListStore = gtk.ListStore(str)
        self.allWidgets['cbFilterYear'].set_model(self.yearListStore)
        cell = gtk.CellRendererText()
        self.allWidgets['cbFilterYear'].pack_start(cell, True)
        self.allWidgets['cbFilterYear'].add_attribute(cell, 'text', 0)

    def fillComboBoxFilterYear(self, year=None):
        """
        Fill combo box for filter (year).
        """
        self.yearListStore.clear()
        years = db.getRecordsYears()
        this_year = "%s" % bd_datetime.Date().date.year
        if not this_year in years:
            years.append(this_year)
        years.sort()
        for year_ in years:
            self.yearListStore.append([year_])
        if year:
            i = 0
            for y in self.yearListStore:
                if y[0] == year:
                    break
                else:
                    i+=1
            self.allWidgets['cbFilterYear'].set_active(i)

    def prepareComboBoxFilterMonth(self):
        self.monthListStore = gtk.ListStore(str, str)
        self.allWidgets['cbFilterMonth'].set_model(self.monthListStore)
        cell = gtk.CellRendererText()
        self.allWidgets['cbFilterMonth'].pack_start(cell, True)
        self.allWidgets['cbFilterMonth'].add_attribute(cell, 'text', 1)

    def fillComboBoxFilterMonth(self, month=''):
        """
        Fill combo box for filter (month).
        """
        self.monthListStore.clear()
        months =  {
                '01': 'Leden',
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
        mkeys = months.keys()
        mkeys.sort()
        for month_ in mkeys:
            self.monthListStore.append([month_, months[month_]])
        if month:
            i = 0
            for m in self.monthListStore:
                if m[0] == month:
                    break
                else:
                    i+=1
            self.allWidgets['cbFilterMonth'].set_active(i)

    def prepareComboBoxDocumentType(self):
        log.debug("prepareComboBoxDocumentType()")
        self.documentTypeListStore = gtk.ListStore(str, str)
        self.allWidgets['cbDocumentType'].set_model(self.documentTypeListStore)
        cell = gtk.CellRendererText()
        self.allWidgets['cbDocumentType'].pack_start(cell, True)
        self.allWidgets['cbDocumentType'].add_attribute(cell, 'text', 1)
        self.fillComboBoxDocumentType()


    def fillComboBoxDocumentType(self):
        log.debug("fillComboBoxDocumentType()")
        # block signal handler when filling cbDocumentType
        self.allWidgets['cbDocumentType'].handler_block_by_func(self.cbDocumentType_changed)
        self.documentTypeListStore.clear()
        document_types = {
                'PPD': "Příjmový pokladní doklad",
                'JV': "Jednoduchý výpis",
                }
        dkeys = document_types.keys()
        for type_ in dkeys:
            self.documentTypeListStore.append([type_, document_types[type_]])
        document_type = db.getConfVal("wSummary_cbDocumentType", 'PPD')
        i = 0
        for t in self.documentTypeListStore:
            if t[0] == document_type:
                break
            else:
                i+=1
        self.allWidgets['cbDocumentType'].set_active(i)
        # unblock signal handler
        self.allWidgets['cbDocumentType'].handler_unblock_by_func(self.cbDocumentType_changed)

    def cbDocumentType_changed(self, widget):
        log.debug("cbDocumentType_changed()")
        self.markClientsInClientsTable()

    def markClientsInClientsTable(self):
        log.debug("markClientsInClientsTable()")
#        print 
        self.allWidgets['tvClientsTable'].get_selection().unselect_all()
        i = 0
        for client_id,_ in self.clientsListStore:
            client = db.getClient(db_id=client_id)
            if client.getPreference('cbDocumentType', 'PPD') == \
                    self.allWidgets['cbDocumentType'].get_active_text():
                self.allWidgets['tvClientsTable'].get_selection().select_path(i)
            i += 1


    def prepareClientsTable(self):
        """
        Prepare clients table.
        """
        log.debug("prepareClientsTable()")
        self.allWidgets['tvClientsTable'].get_selection().set_mode(gtk.SELECTION_MULTIPLE)

        self.clientsListStore = gtk.ListStore(
                int,
                str,
                )
        self.allWidgets['tvClientsTable'].set_model(self.clientsListStore)
        column_client = gtk.TreeViewColumn("Klient",
                gtk.CellRendererText(),
                text=1)
        self.allWidgets['tvClientsTable'].append_column(column_client)

        self.fillClientsTable()

    def fillClientsTable(self):
        """
        Fill clients to the table.
        """
        log.debug("fillClientsTable()")
        year = self.allWidgets['cbFilterYear'].get_active_text()
        month = self.allWidgets['cbFilterMonth'].get_active_text()

        clients = db.getClientsOfRecords(year=year, month=month)
#        pprint(clients)
        self.clientsListStore.clear()
        for client in clients:
            self.clientsListStore.append([
                    client.db_id,
                    "%s %s" % (client.last_name, client.first_name),
                    ])
        # Sort clients table
        self.clientsListStore.set_sort_column_id(1, gtk.SORT_ASCENDING)
        self.markClientsInClientsTable()

    def calendarWindowIssue(self, widget):
        """
        Open window with calendar.
        """
        log.debug("calendarWindowIssue()")
        date = dialogCalendar(self.w)
        if date:
            self.allWidgets['eDateIssue'].set_text(date)

    def calendarWindowPayment(self, widget):
        """
        Open window with calendar.
        """
        log.debug("calendarWindowPayment()")
        date = dialogCalendar(self.w)
        if date:
            self.allWidgets['eDatePayment'].set_text(date)


    def saveSummary(self, widget):
        """
        Create summary.
        """
        db.setConf("wSummary_eClerkName", \
                self.allWidgets['eClerkName'].get_text(),
                "Doklad vystavil")
        db.setConf("wSummary_cbDocumentType", \
                self.allWidgets['cbDocumentType'].get_active_text(),
                "Typ vystavovaného dokladu")
        self.allWidgets['tvClientsTable'].get_selection().selected_foreach(self.callback_selected_foreach)
        
        if not self.clients:
            return

        year = self.allWidgets['cbFilterYear'].get_active_text()
        month = self.allWidgets['cbFilterMonth'].get_active_text()
        document_type = self.allWidgets['cbDocumentType'].get_active_text()
        date_issue = self.allWidgets['eDateIssue'].get_text()
        date_payment = self.allWidgets['eDatePayment'].get_text()
        clerk_name = self.allWidgets['eClerkName'].get_text()
        code_fixed = self.allWidgets['eCodeFixed'].get_text()
        code_variable = self.allWidgets['eCodeVariable'].get_text()

        file_name_suggestion = ""
        # suggestion for name of output file
        if document_type == "PPD":
            file_name_suggestion = "Prijmovy_pokladni_doklad_%s_%s" % (month, year)
        elif document_type == "JV":
            file_name_suggestion = "Sestava_%s_%s" % (month, year)

        # path to output file without extension
        output_file = self.dialogSaveSummary(file_name_suggestion)
        log.debug("Path for saving summary: %s" % output_file)
        if not output_file:
            return

        summary = bd_summary.Summary(year=year, month=month, \
                clients=self.clients, 
                document_type=document_type,
                date_issue=date_issue,
                date_payment=date_payment,
                clerk_name=clerk_name,
                code_fixed=code_fixed,
                code_variable=code_variable,
                output_file = output_file
                )

        print summary
        import bd_pdf
        pdf = bd_pdf.PdfSummary(summary)
        pdf.createPdfSummary()



        self.clients = []
#        self.w.destroy()

    def callback_selected_foreach(self, treemodel, path, iter):
        log.debug("callback_selected_foreach()")
        client_id = self.clientsListStore.get_value(iter, 0)
        self.clients.append(client_id)




    def nothing(self, widget, parameters=None):
        log.debug("Do nothing (parameters: %s)"%parameters)


    def dialogSaveSummary(self, file_name=None):
        """
        Open dialog for saving Summary.
        Return File path (without extension) or None.
        """
        log.debug('WSummary.dialogSaveSummary()')

        # filters for listed files in dialog
        file_filter = {}
        file_filter['pdf'] = gtk.FileFilter()
        file_filter['pdf'].add_pattern('*.pdf')
        file_filter['vse'] = gtk.FileFilter()
        file_filter['vse'].add_pattern('*')

        # change filter of listed files
        def on_wSaveSummary_cbFileType_changed(widget, data=None):
            if wSaveSummary_cbFileType.get_active() == 0:
                self.wSaveSummary.set_filter(file_filter['pdf'])
            else:
                self.wSaveSummary.set_filter(file_filter['vse'])
                

        # xml tree for dialog
        wSaveSummaryxml = gtk.glade.XML(GLADEFILE, "wSaveSummary")
        self.wSaveSummary = wSaveSummaryxml.get_widget("wSaveSummary")
        # box for chose type of file
        wSaveSummary_cbFileType = \
                wSaveSummaryxml.get_widget("wSaveSummary_cbFileType")
        # fulfilment of box for file type selection
        ls_model = gtk.ListStore(str)
        ls_model.append(["PDF dokumenty(*.pdf)"])
        ls_model.append(["Všechny soubory"])
        wSaveSummary_cbFileType.set_model(ls_model)
        cell = gtk.CellRendererText()
        wSaveSummary_cbFileType.pack_start(cell)
        wSaveSummary_cbFileType.add_attribute(cell,'text',0)
        wSaveSummary_cbFileType.set_active(0)
        # connect signal for change
        wSaveSummary_cbFileType.connect('changed', \
                on_wSaveSummary_cbFileType_changed)
        # set default filter to 'pdf'
        self.wSaveSummary.set_filter(file_filter['pdf'])   

        # last path
        last_summary_path = db.getConfVal('last_summary_path', '.')
        self.wSaveSummary.set_current_folder(last_summary_path)

        # suggested filename 
        if file_name:
            self.wSaveSummary.set_current_name(file_name)

        # run dialog
        returned_value = self.wSaveSummary.run()
        
        # check selected file
        if returned_value == gtk.RESPONSE_OK and self.wSaveSummary.get_filename():
            file_path = self.wSaveSummary.get_filename().decode("utf-8")
            file_path = os.path.splitext(file_path)[0]

            self.wSaveSummary.destroy()

            # save last position in directories tree
            db.setConf(name="last_summary_path", \
                    value=os.path.split(file_path)[0], \
                    note="Path to directory with last saved summary.")

            return file_path
        else:
            self.wSaveSummary.destroy()
            return None







class WSettings():
    """
    BeneDat settings window.
    """
    def __init__(self):
        # Window
        self.wxml = gtk.glade.XML(GLADEFILE, "wSettings")
        self.w = self.wxml.get_widget("wSettings")

        # Signals
        signals = {
                "on_wSettings_destroy": self.nothing,
                "on_wSettings_btCancel_clicked": self.closeWSettings,
                "on_wSettings_btApply_clicked": self.applyWSettings,
                "on_wSettings_btSave_clicked": self.saveWSettings,
                }
        self.wxml.signal_autoconnect(signals)

        # Widgets
        self.allWidgets = {}
        self.ewidgets = (
                # Editable fields
                'eHoursLevelOS1',
                'eHoursLevelOS2',
                'eHoursLevelChB1',
                'eHoursLevelChB2',
                'eTransportPriceFuel',
                'eTransportExp',
                'eTransportK',
                'eTransportEntryRate',
                'eTransportClientPart',
                'eTransportPriceChM',
                'eDietRefreshmentCh',
                'eDietRefreshmentM',
                'eDietLunchCh',
                'eDietLunchM',
                'eDietBreakfastM',
                'eDietDinnerM',
                'eBilletChB1',
                'eBilletChB2',
                'eBilletChB3',
                'eBilletOS',
                'eSummaryCodeFixed',
                'eSummaryCodeVariable',
                'eSummaryTill',
                'eAccountOS',
                'eAccountOSBillet',
                'eAccountChB',
                'eAccountChBBillet',
                'eAccountBillet',
                'eAccountTransportClients',
                'eAccountRefreshment',
                'eAccountLunch',
                'eAccountBreakfast',
                'eAccountDinner',
                'eAccountDiet',
                )
        widgets = (
                # TextView
                'teSummaryAddress',
                'teSummaryInformation',
                # Buttons
                'btCancel',
                'btApply',
                'btSave',
                )
        for widget in self.ewidgets + widgets:
            self.allWidgets[widget] = self.wxml.get_widget("wSettings_%s"%widget)

        self.textBuffers = {}
        for widget in ('teSummaryAddress', 'teSummaryInformation'):
            w = self.wxml.get_widget("wSettings_%s"%widget)
            self.textBuffers[widget] = w.get_buffer()


        # load configuration and fill fields
        self.loadSettings()


    def run(self):
        log.debug("<wSettings>.w.show_all()")
        self.w.show_all()

    def closeWSettings(self, widget):
        """
        """
        log.debug("closeWSettings()")
        self.w.destroy()

    def applyWSettings(self, widget):
        """
        """
        log.debug("applyWSettings()")
        self.saveSettings()

    def saveWSettings(self, widget):
        """
        """
        log.debug("saveWSettings()")
        self.saveSettings()
        self.closeWSettings(widget=None)

    def saveSettings(self):
        """
        """
        log.debug("saveSettings()")
        # save Editable fields
        for widget in self.ewidgets:
            log.debug("Saving configuration '%s' - %s." % \
                    (widget, eSettings[widget]))
            db.setConf(name=widget, \
                    value=self.allWidgets[widget].get_text(), \
                    note=eSettings[widget],
                    commit=False)
            
        # save TextView fields
        for widget in ('teSummaryAddress', 'teSummaryInformation'):
            db.setConf(name=widget, \
                    value=self.textBuffers[widget].get_text( \
                            *self.textBuffers[widget].get_bounds()), \
                    note=teSettings[widget],
                    commit=False)
            
        db.commit()

    def loadSettings(self):
        """
        """
        log.debug("loadSettings()")
        # load Editable fields
        for widget in self.ewidgets:
            log.debug("Loading configuration '%s' - %s." % \
                    (widget, eSettings[widget]))
            self.allWidgets[widget].set_text( \
                    db.getConfVal(name=widget, default=""))
            
        # load TextView fields
        for widget in ('teSummaryAddress', 'teSummaryInformation'):
            log.debug("Loading configuration '%s' - %s." % \
                    (widget, teSettings[widget]))
            self.textBuffers[widget].set_text( \
                    db.getConfVal(name=widget, default=""))
          



    def nothing(self, widget, parameters=None):
        log.debug("Do nothing (parameters: %s)"%parameters)





class DCalendar:
    """
    Calendar window.
    """
    def __init__(self, ancestor=None):
        self.actual = ""
        self.dialog = gtk.Dialog ("Kalendář", ancestor,
            gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_MODAL, \
            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, \
            gtk.RESPONSE_OK))
        self.calendar = gtk.Calendar()
        self.dialog.vbox.pack_start(self.calendar, True, True, 0)
        self.calendar.connect('day_selected_double_click',\
                self.day_selected_double_click, self.dialog)
        timestamp = time.localtime()
        if timestamp:
            self.calendar.select_month(timestamp[1] - 1, timestamp[0])
            self.calendar.select_day(timestamp[2])
        self.dialog.show_all()
        result = self.dialog.run()
        if result == gtk.RESPONSE_OK:
            self.check_date(self.calendar, self.dialog)
        else:
            self.dialog.destroy()

    def day_selected_double_click(self, widget, dialog):
        self.check_date(widget, dialog)

    def check_date(self, widget, dialog):
        (year, month, day) = widget.get_date()
        self.actual = str(day) + '.' + str(month+1) + '.' + str(year)
        self.dialog.destroy()

def dialogCalendar(predek = None):
    """
    Open window in calendar.
    """
    calendar =  DCalendar(predek)
    return calendar.actual



class DQuestion:
    """
    Dilog with question.
    """
    def __init__(self, text="", secondary_text="", title="Otázka"):
        dialog = gtk.MessageDialog(None,
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO,str(text))
        dialog.set_property("secondary-text", secondary_text)
        dialog.set_property("title", title)
        self.return_value = dialog.run()
        dialog.destroy()

def dialogQuestion(text="", secondary_text="", title="Otázka"):
    dialog = DQuestion(text, secondary_text, title)
    return dialog.return_value





# vim:tabstop=4:shiftwidth=4:softtabstop=4:
# eof
