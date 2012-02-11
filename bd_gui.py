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

import bd_config
import bd_database





# get configuration
conf = bd_config.getConfig()

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
                "on_wMain_btSettings_clicked": self.openWSettings,
                "on_wMain_btExit_clicked": self.exit,
                }

        self.wxml.signal_autoconnect(signals)




    def exit(self, widget):
        """
        Exit BeneDat.
        """
        gtk.main_quit()

    def openWRecords(self, widget):
        """
        Open window for records.
        """
        pass

    def openWSummary(self, widget):
        """
        Open window for summary.
        """
        pass

    def openWClients(self, widget):
        """
        Open window for clients.
        """
        pass

    def openWSettings(self, widget):
        """
        Open window for clients.
        """
        windowSettings = wSettings()
        windowSettings.run()

    def dialogNewDb(self, widget):
        """
        Open dialog for new db.
        """
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
            print conf.get('main', 'last_open_file')

            self.wNewDB.destroy()

            # create new db
            db =  bd_database.getDb(db_file=conf.get('main', 'last_open_file'),
                    new=True)
        else:
            self.wNewDB.destroy()
    






    def dialogOpenDb(self, widget):
        """
        Open dialog for open db.
        """
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
            print conf.get('main', 'last_open_file')
            self.wOpenDB.destroy()
            # Open db
            if db:
                db.open_database(db_file=conf.get('main', 'last_open_file'))
            else:
                db =  bd_database.getDb(db_file=conf.get('main', 'last_open_file'))
        else:
            self.wOpenDB.destroy()
    



    def dialogEmptyDbCOpy(self, widget):
        """
        Open dialog for copy empty db.
        """
        pass





class wSettings():
    """
    BeneDat settings window.
    """
    def __init__(self):
        self.wxml = gtk.glade.XML(GLADEFILE, "wSettings")
        self.w = self.wxml.get_widget("wSettings")



    def run(self):
        self.w.show_all()







# vim:tabstop=4:shiftwidth=4:softtabstop=4:
# eof
