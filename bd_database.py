#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Helpful module for work with database.

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

VERSION_DB = 0

import sqlite3
import os

from bd_exceptions import *


# variable with actual object of class Db
__db = None


def getDb(db_file=None, new=False):
    """
    Parameters are the same as in Db.__init__().
    First call of getDb have to contain db_file, 
    in further calls db_file and new have no effect.
    """
    global __db
    if not __db:
      __db=Db(db_file=db_file, new=new)
    return __db


class Db():
    def __init__(self, db_file, new=False):
        """
        Open existing or create new database file. 
        If 'new'=True, old file is removed and new created.
        """
        # variable for database connection
        self.__dbcon = None
        # variable for connection cursor 
        self.__dbc = None
        
        # if new = True, remove old file
        if new and os.path.isfile(db_file):
            os.remove(db_file)
        
        # if db_file exists - open it otherwise create it
        if os.path.isfile(db_file):
            self.open_database(db_file)
        else:
            self.create_database(db_file)
    
    def __del__(self):
        """
        Closing database on exit.
        """
        if type(self.__dbc) == sqlite3.Cursor:
            self.__dbc.close()
        if type(self.__dbcon) == sqlite3.Connection:
            self.__dbcon.close()
    

    def create_database(self, db_file):
        """
        Create new database and insert initial data.
        """
        # create database file
        try:
            self.__dbcon = sqlite3.connect(db_file)
            self.__dbc = self.__dbcon.cursor()
            self.__dbcon.text_factory = lambda x: unicode(x, "utf-8", "ignore")
        except sqlite3.OperationalError as e:
            raise bdFileError("Nemohu vytvořit soubor %s! (%s)" % (db_file, e))

        # create database schema
        try:
            # create configuration table 
            self.__dbc.execute("""
                CREATE TABLE configuration(
                    name TEXT NOT NULL,
                    value TEXT,
                    note TEXT, 
                    PRIMARY KEY (name)
                    );                    
            """
            )
            self.__dbc.commit()
        except sqlite3.Error, e:
            raise bdDbError("Problém s vytvořením databázové struktury.")

        # insert initial schema
        try:
            pass
        except sqlite3.Error, e:
            raise bdDbError("Problém s vložením výchozího nastavení.")

    
    def open_database(self, db_file):
        # open database file
        try:
            self.__dbcon = sqlite3.connect(db_file)
            self.__dbc = self.__dbcon.cursor()
            self.__dbcon.text_factory = lambda x: unicode(x, "utf-8", "ignore")
        except sqlite3.OperationalError as e:
            raise bdFileError("Nemohu otevřít soubor %s! (%s)" % (db_file, e))
        # TODO: ověření db









# vim:tabstop=4:shiftwidth=4:softtabstop=4:
# eof
