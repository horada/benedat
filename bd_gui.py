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
from pprint import pprint

import bd_config
import bd_clients
import bd_database
from bd_descriptions import eSettings,teSettings
import bd_logging
from bd_logging import rnl





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

        self.columns = {}
        self.columns['id'] = gtk.TreeViewColumn("ID",
                gtk.CellRendererText(),
                text=0)
        self.columns['firstName'] = gtk.TreeViewColumn("Jméno",
                gtk.CellRendererText(),
                text=1)
        self.columns['lastName'] = gtk.TreeViewColumn("Příjmení",
                gtk.CellRendererText(),
                text=2)
        self.columns['address'] = gtk.TreeViewColumn("Adresa",
                gtk.CellRendererText(),
                text=3)
        self.columns['phone'] = gtk.TreeViewColumn("Telefon",
                gtk.CellRendererText(),
                text=4)
        self.columns['mobilePhone1'] = gtk.TreeViewColumn("Mobil 1",
                gtk.CellRendererText(),
                text=5)
        self.columns['mobilePhone2'] = gtk.TreeViewColumn("Mobil 2",
                gtk.CellRendererText(),
                text=6)
        self.columns['notes'] = gtk.TreeViewColumn("Poznámka",
                gtk.CellRendererText(),
                text=7)
        self.columns['distance'] = gtk.TreeViewColumn("Vzdálenost",
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
            self.allWidgets['tvClientsTable'].append_column(self.columns[column])
        
        # configure searching 
        self.columns['id'].set_sort_column_id(0)
        self.columns['lastName'].set_sort_column_id(2)
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
                "on_wRecords_btDate_clicked": self.nothing,
                "on_wRecords_btAddService_clicked": self.addService,
                "on_wRecords_btSaveRecord_clicked": self.saveRecord,
                }
        self.wxml.signal_autoconnect(signals)

        # Widgets
        self.allWidgets = {}
        widgets = (
                'cbFilterMonth',
                'cbFilterYear',
                'eClient',
                'eDate',
                'tabServices',
                'btAddService'
                )
        for widget in widgets:
            self.allWidgets[widget] = self.wxml.get_widget("wRecords_%s"%widget)

        # create clients menu
        self.createClientsMenu()

        # setup completion
        self.clientEntryCompletion()

        # add one "line" for services
        self.addService(None)

        # put cursor to the eClient field
        self.allWidgets['eClient'].grab_focus()

    def run(self):
        log.debug("<WRecords>.w.show_all()"%self)
        self.w.show_all()


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
            c_item[c].connect_object("activate", self.nothing, c)
            self.MenuClients.append(c_item[c])

        self.MenuClients.show_all()

    def clientsMenu(self, widget):
        """
        Popup menu with list of clients.
        """
        self.MenuClients.popup(None, None, None, 0, 0)

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

    def serviceTypeCompletion(self, ewidget):
        """
        Set up entry completion for service type entry.
        """
        completion = gtk.EntryCompletion()

        servicesListStore = gtk.ListStore(
                str, # Servyce type
                )
        # TODO: - where to find properly services?
        services = ('OS', 'STD', 'ChB')
        for service in services:
            servicesListStore.append([service])

        completion.set_model(servicesListStore)
        completion.set_text_column(0)
        completion.set_minimum_key_length(0)
        ewidget.set_completion(completion)


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
#        service['type'] = gtk.Entry()
#        service['type'].set_width_chars(4)
#        service['type'].set_max_length(4)
#        self.serviceTypeCompletion(service['type'])
        self.allWidgets['tabServices'].attach(service['type'], \
                0,1,top_attach, bottom_attach)
        # from time 
        service['from'] = gtk.Entry()
        service['from'].set_width_chars(5)
        service['from'].set_max_length(5)
        self.allWidgets['tabServices'].attach(service['from'], \
                1,2,top_attach, bottom_attach)
        # to time
        service['to'] = gtk.Entry()
        service['to'].set_width_chars(5)
        service['to'].set_max_length(5)
        self.allWidgets['tabServices'].attach(service['to'], \
                2,3,top_attach, bottom_attach)
        # remove button
        service['remove'] = gtk.Button(label="-")
        service['remove'].connect('clicked', self.deleteService, i)
        self.allWidgets['tabServices'].attach(service['remove'], \
                3,4,top_attach, bottom_attach)
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






class DialogQuestion:
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
    dialog = DialogQuestion(text, secondary_text, title)
    return dialog.return_value





# vim:tabstop=4:shiftwidth=4:softtabstop=4:
# eof
