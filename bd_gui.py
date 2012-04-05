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
        log.debug('gtk.main_quit()')
        gtk.main_quit()

    def openWRecords(self, widget):
        """
        Open window for records.
        """
        log.debug('openWRecords()')
        windowRecords= WRecords()
        windowRecords.run()

    def openWSummary(self, widget):
        """
        Open window for summary.
        """
        log.debug('openWSummary()')
        pass

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
                'tvClientsTable'
                )
        for widget in widgets:
            self.allWidgets[widget] = self.wxml.get_widget("wClients_%s"%widget)

        # connect signal for select row by simple click
        self.allWidgets['tvClientsTable'].get_selection().connect('changed',self.cursorChanged)

        # Prepare and fill table of clients
        self.prepareClientsTable()

        # put cursor to the FirstName field
        self.allWidgets['eFirstName'].grab_focus()

    def run(self):
        log.debug("<wClients>.w.show_all()"%self)
        self.w.show_all()
        
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
                int, # distance
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
        columns['distance'] = gtk.TreeViewColumn("Vzdálenost",
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
                'distance',
                )
        for column in columns_order:
            self.allWidgets['tvClientsTable'].append_column(columns[column])
        
        # configure sorting and searching
        columns['id'].set_sort_column_id(0)
        columns['lastName'].set_sort_column_id(2)
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
                    client.getPreferenceInt('distance', 0),
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
            db.delClient(self.actual_client.db_id)
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
            ac.setPreference("distance",self.allWidgets["eDistance"].get_text())
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
                    preferences={"distance":self.allWidgets["eDistance"].get_text()})
            log.info(rnl('Create new client %s' % repr(self.actual_client)))
            #TODO: check if similar client not exist
            db.addClient(self.actual_client)
        self.newClient()
        self.fillClientsTable()
        # put cursor to the firstName field
        self.allWidgets['eFirstName'].grab_focus()
        

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
        self.allWidgets["eDistance"].set_text("%s" % self.actual_client.getPreferenceInt('distance', 0))
 


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
                )
        for e in editable_fields:
            self.allWidgets[e].set_text('')

    def cursorChanged(self, selected):
        log.debug("cursorChanged(%s)" % selected)
        (model,iter) = selected.get_selected()
        if iter:
            client_id = self.clientsListStore.get_value(iter, 0)
            self.fillClientForm(client_id)

    def nothing(self, widget, parameters=None):
        log.debug("Do nothing (parameters: %s)"%parameters)


class WRecords():
    """
    BeneDat records window
    """
    def __init__(self):
        # Actual record
        self.actual_record = None

        # widgets for services
        self.services = {}

        # Window
        self.wxml = gtk.glade.XML(GLADEFILE, "wRecords")
        self.w = self.wxml.get_widget("wRecords")

        # Signals
        signals = {
                "on_wRecords_btNewRecord_clicked": self.newRecord,
                "on_wRecords_btDeleteRecord_clicked": self.deleteRecord,
                "on_wRecords_btClose_clicked": self.closeWRecords,
                "on_wRecords_destroy": self.closeWRecords,
                "on_wRecords_tbtFilter_toggled": self.nothing,
                "on_wRecords_cbFilterMonth_changed": self.nothing,
                "on_wRecords_cbFilterYear_changed": self.nothing,
                "on_wRecords_btClient_clicked": self.clientsMenu,
                "on_wRecords_btDate_clicked": self.calendarWindow,
                "on_wRecords_btAddService_clicked": self.addService,
                "on_wRecords_btSaveRecord_clicked": self.saveRecord,
                "on_wRecords_eDate_focus_out_event": self.nothing,
                "on_wRecords_eDate_key_release_event":self.eDate_key_release,
                }
        self.wxml.signal_autoconnect(signals)

        # Widgets
        self.allWidgets = {}
        widgets = (
                'cbFilterMonth',
                'cbFilterYear',
                'tvRecordsTable',
                'eClient',
                'eDate',
                'tabServices',
                'btAddService',
                'eClient',
                'eDate',
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
                )
        for widget in widgets:
            self.allWidgets[widget] = self.wxml.get_widget("wRecords_%s"%widget)

        # connect signal for select row by simple click
        self.allWidgets['tvRecordsTable'].get_selection().connect('changed',self.cursorChanged)

        # prepare and fill table of records
#        self.prepareRecordsTable()

        # create clients menu
        self.createClientsMenu()

        # setup completion
        self.clientEntryCompletion()

        # add one "line" for services
        self.addService(None)

        # put cursor to the eClient field
        self.allWidgets['eClient'].grab_focus()

        # TODO: this remove, the above uncomment
        self.prepareRecordsTable()

    def run(self):
        log.debug("<WRecords>.w.show_all()"%self)
        self.w.show_all()

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
                str, # 6 transport
                str, # 7 diet
                str, # 8 billet
                #
                str, # 9 date for sorting
                )
        self.allWidgets['tvRecordsTable'].set_model(self.recordsListStore)

        columns = {}
        columns['name'] = gtk.TreeViewColumn("Jméno",
                gtk.CellRendererText(),
                text=1)
        columns['date'] = gtk.TreeViewColumn("Datum",
                gtk.CellRendererText(),
                text=2)
        columns['service_type'] = gtk.TreeViewColumn("Služba",
                gtk.CellRendererText(),
                text=3)
        columns['time_from'] = gtk.TreeViewColumn("Čas od",
                gtk.CellRendererText(),
                text=4)
        columns['time_to'] = gtk.TreeViewColumn("Čas do",
                gtk.CellRendererText(),
                text=5)
        columns['transport'] = gtk.TreeViewColumn("Doprava",
                gtk.CellRendererText(),
                text=6)
        columns['diet'] = gtk.TreeViewColumn("Strava",
                gtk.CellRendererText(),
                text=7)
        columns['billet'] = gtk.TreeViewColumn("Ubytování",
                gtk.CellRendererText(),
                text=8)

        columns_order = (
                'name',
                'date',
                'service_type',
                'time_from',
                'time_to',
                'transport',
                'diet',
                'billet',
                )
        for column in columns_order:
            self.allWidgets['tvRecordsTable'].append_column(columns[column])

        # configure sorting and searching
        columns['name'].set_sort_column_id(1)
        columns['date'].set_sort_column_id(9)
        self.allWidgets['tvRecordsTable'].set_enable_search(True)
        self.allWidgets['tvRecordsTable'].set_search_column(2)
        self.fillRecordsTable()

    def fillRecordsTable(self):
        """
        Fill records to the table.
        """
        log.debug("fillRecordsTable()")
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
            value_records = {
                    'transport': "%s%s%s%s %skč" % (
                        x(vrs['TOS'].value),
                        x(vrs['TFS'].value),
                        x(vrs['TChMo'].value),
                        x(vrs['TMoCh'].value),
                        vrs['TSO'].value,
                        ),
                    'diet': "%s%s%s%s%s%s %skč" % (
                        x(vrs['DRCh'].value),
                        x(vrs['DRM'].value),
                        x(vrs['DLCh'].value),
                        x(vrs['DLM'].value),
                        x(vrs['DBM'].value),
                        x(vrs['DDM'].value),
                        vrs['DO'].value,
                        ),
                    'billet': "%s%s%s%s %skč" % (
                        x(vrs['BChB1'].value),
                        x(vrs['BChB2'].value),
                        x(vrs['BChB3'].value),
                        x(vrs['BOS'].value),
                        vrs['BO'].value,
                        )}

            # fill records
            self.recordsListStore.append([
                    record.db_id,
                    "%s %s" % (record.client.last_name, record.client.first_name),
                    "%s" % record.date,
                    time_records['service_type'].strip(),
                    time_records['time_from'].strip(),
                    time_records['time_to'].strip(),
                    value_records['transport'],
                    value_records['diet'],
                    value_records['billet'],
                    "%s" % record.date,
                    ])




    def closeWRecords(self, widget):
        """
        """
        log.debug("closeWRecords()")
        self.w.destroy()


    def newRecord(self, widget):
        """
        Clear input field and set actual_record to None.
        """
        log.debug("newRecord()")
        self.actual_record = None

    def deleteRecord(self, widget):
        """
        Delete actually selected record.
        """
        log.debug("deleteRecord(): %s" % repr(self.actual_record))
        if not self.actual_record:
            return
        result = dialogQuestion(text="Opravdu si přejete smazat záznam:",
                secondary_text="%s %s" % (self.actual_record.client.first_name, 
                    self.actual_client.client.last_name),
                title="[BeneDat] Dotaz - smazání záznamu")


    def saveRecord(self, widget):
        """
        Save selected/created record.
        """
        log.debug("saveRecord(): %s" % repr(self.actual_record))
        # check filled fields
        client = db.getClient(name=self.allWidgets['eClient'].get_text())
        if not client:
            return
        # TODO: check filled fields

        # update existing or add new record
        if self.actual_record:
            # update existing record
            ar = self.actual_record
            # TODO: update actual record
        else:
            # create (add) new record
            self.actual_record = bd_records.Record(
                    client = client,
                    date = self.allWidgets['eDate'].get_text())
            # insert time records
            for key in self.services:
                self.actual_record.addTimeRecord(
                        service_type=self.services[key]['type']. \
                                get_active_text(),
                        time_from=self.services[key]['from'].get_text(),
                        time_to=self.services[key]['to'].get_text())
            # insert value records
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

######################################
# TSO       eTransportServiceOther
# DO        eDietOther
# BO        eBilletOther
# TOS       chTransportOnService
# TFS       chTransportFromService
# TChMo     chTransportChMo
# TMoCh     chTransportMoCh
# DRCh      chDietRefreshmentCh
# DRM       chDietRefreshmentM
# DLCh      chDietLunchCh
# DLM       chDietLunchM
# DBM       chDietBreakfastM
# DDM       chDietDinnerM
# BChB1     chBilletChB1
# BChB2     chBilletChB2
# BChB3     chBilletChB3
# BOS       chBilletOS
######################################
            print self.actual_record
            log.info(rnl('Create new record %s' % repr(self.actual_record)))
            db.addRecord(self.actual_record)
            self.fillRecordsTable()

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
        log.debug("calendarWindow")
        date = dialogCalendar(self.w)
        if date:
            self.allWidgets['eDate'].set_text(date)

    def eDate_key_release(self, widget, parameters):
        """
        """
        if parameters.string in ('+', '-'):
            widget.set_text(widget.get_text().replace('-','').replace('+',''))
            # TODO update date
            
    def serviceFillComboBox(self, cbwidget):
        """
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



    def addService(self, widget):
        """
        Add widget for service ...
        """
        if self.services:
            i = max(self.services.keys()) + 1
        else:
            i = 0
        log.debug("Removing widgets for service (id=%s)."%i)
        top_attach = i+1
        bottom_attach = i+2
        service = {}
        # service type
        service['type'] = gtk.ComboBox()
        self.serviceFillComboBox(service['type'])
        self.allWidgets['tabServices'].attach(service['type'], \
                0,1,top_attach, bottom_attach, \
                xoptions=gtk.FILL, yoptions=gtk.FILL)
        # from time 
        service['from'] = gtk.Entry()
        service['from'].set_width_chars(5)
        service['from'].set_max_length(5)
        self.allWidgets['tabServices'].attach(service['from'], \
                1,2,top_attach, bottom_attach, \
                xoptions=gtk.FILL, yoptions=gtk.FILL)
        # to time
        service['to'] = gtk.Entry()
        service['to'].set_width_chars(5)
        service['to'].set_max_length(5)
        self.allWidgets['tabServices'].attach(service['to'], \
                2,3,top_attach, bottom_attach, \
                xoptions=gtk.FILL, yoptions=gtk.FILL)
        # remove button
        service['remove'] = gtk.Button(label=" - ")
        service['remove'].connect('clicked', self.deleteService, i)
        self.allWidgets['tabServices'].attach(service['remove'], \
                3,4,top_attach, bottom_attach, \
                xoptions=gtk.FILL, yoptions=gtk.FILL)
        # show all widgets
        self.allWidgets['tabServices'].show_all()
        # put cursor to the first added field
        service['type'].grab_focus()
        # add service between all services
        self.services[i]= service

    def deleteService(self, widget, id_):
        """
        Delete widgets for service ...
        """
        log.debug("Adding widgets for service (id=%s)."%id_)
        self.allWidgets['tabServices'].remove(self.services[id_]['type'])
        self.allWidgets['tabServices'].remove(self.services[id_]['from'])
        self.allWidgets['tabServices'].remove(self.services[id_]['to'])
        self.allWidgets['tabServices'].remove(self.services[id_]['remove'])
        self.allWidgets['btAddService'].grab_focus()
        del self.services[id_]

    def cursorChanged(self, selected):
        log.debug("cursorChanged(%s)" % selected)
        (model,iter) = selected.get_selected()
#        if iter:
#            record_id = self.recordsListStore.get_value(iter, 0)
#            self.fillRecordForm(client_id)




    def nothing(self, widget, parameters=None):
        log.debug("Do nothing (parameters: %s)"%parameters)





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
        log.debug("<wSettings>.w.show_all()"%self)
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
        self.closeWSettings(None)

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
