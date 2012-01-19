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

DB_MAJOR_VERSION = 2
DB_VERSION = 0

INITIAL_CONFIGURATION = (
        {'name':'db_major_version',
        'value': DB_MAJOR_VERSION,
        'note':'Major version of database.'},
        {'name':'db_version',
        'value': DB_VERSION,
        'note':'Version of database.'},
#        {'name':'',
#        'value':'',
#        'note':''},
        )

import sqlite3
import os
import sys

from bd_exceptions import *
import bd_clients


# variable with actual object of class Db
db = None


def getDb(db_file=None, new=False):
    """
    Parameters are the same as in Db.__init__().
    First call of getDb have to contain db_file, 
    in further calls db_file and new have no effect.
    """
    global db
    if not db:
      db=Db(db_file=db_file, new=new)
    return db


class Db():
    def __init__(self, db_file, new=False):
        """
        Open existing or create new database file. 
        If 'new'=True, old file is removed and new created.
        """
        # variable for database connection
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
        global db
        print db
        if type(self.__dbc) == sqlite3.Connection:
            self.__dbc.close()
#        if db is self:
#            db = None
 
    def execute(self, query, data=None):
        """
        Execute database query.
        """
        # variable for connection cursor 
        dbcc = self.__dbc.cursor()
        if data:
            result = dbcc.execute(query, data)
        else:
            result = dbcc.execute(query)
        return result
    
    def commit(self):
        """
        Commit changes to database.
        """
        self.__dbc.commit()
    
    def create_database(self, db_file):
        """
        Create new database and insert initial data.
        """
        # create database file
        try:
            self.__dbc = sqlite3.connect(db_file)
            self.__dbc.text_factory = u
        except sqlite3.OperationalError as e:
            raise bdFileError("Nemohu vytvořit soubor %s! (%s)" % (db_file, e))

        # create database schema
        try:
            # create configuration table 
            self.execute("""
                CREATE TABLE configuration(
                    name TEXT NOT NULL,
                    value TEXT,
                    note TEXT, 
                    PRIMARY KEY (name)
                    );                    
            """
            )
            # create clients table
            self.execute("""
                CREATE TABLE clients(
                    id INTEGER NOT NULL,
                    first_name TEXT,
                    last_name TEXT,
                    address TEXT,
                    phone TEXT,
                    mobile_phone1 TEXT,
                    mobile_phone2 TEXT,
                    notes TEXT,
                    PRIMARY KEY (ID)
                    );                    
            """
            )
            # create records table 
            self.execute("""
                CREATE TABLE records(
                    id INTEGER NOT NULL,
                    client INTEGER NOT NULL,
                    PRIMARY KEY (ID)
                    );                    
            """
            )
            # create timed records table 
            self.execute("""
                CREATE TABLE records_timed(
                    id INTEGER NOT NULL,
                    id_record INTEGER NOT NULL,
                    service TEXT,
                    time_from TEXT,
                    time_to TEXT,
                    PRIMARY KEY (ID)
                    );                    
            """
            )
            # create numeric records table 
            self.execute("""
                CREATE TABLE records_numeric(
                    id INTEGER NOT NULL,
                    id_record INTEGER NOT NULL,
                    service TEXT,
                    value INTEGER,
                    PRIMARY KEY (ID)
                    );                    
            """
            )
            self.commit()
        except sqlite3.Error, e:
            raise bdDbError("Problém s vytvořením databázové struktury: %s" %e)

        # insert initial data 
        try:
            self.updateConfiguration()
            self.commit()
        except sqlite3.Error, e:
            raise bdDbError("Problém s vložením výchozího nastavení: %s" %e)

    def open_database(self, db_file):
        # open database file
        try:
            self.__dbc = sqlite3.connect(db_file)
            self.__dbc.text_factory = u
        except sqlite3.OperationalError as e:
            raise bdFileError("Nemohu otevřít soubor %s! (%s)" % (db_file, e))
        self.verification()

    def verification(self):
        """
        Db verification.
        """
        # TODO: db verification
        try: 
            print self.getConfVal("db_major_version")
            print self.getConfVal("db_version")
        except sqlite3.OperationalError as err:
            print err
            raise



    def updateConfiguration(self, update_set=INITIAL_CONFIGURATION):
        """
        Update configuration in database (insert only non exist items).
        update_set = ({'name':"NAME", 'value':"VALUE", ''note': "NOTE"}, {..},...)
        """
        for item in update_set:
            # check if item is not in database
            if "DOES_NOT_CONTAIN" == \
                    self.getConfVal(item['name'], "DOES_NOT_CONTAIN"):
                # database did not contain this item => insert it
                self.setConf(item['name'], item['value'], item['note'])

    def getConf(self, name=None, pattern_name=None):
        """
        Return configuration along to name, pattern_name or whole configuration.
        """
        if name:
            result = self.execute('''SELECT name,value,note FROM configuration 
                WHERE name=:name''', {'name':name})
            result = result.fetchone()
            if result:
                return [{'name': result[0],
                        'value': result[1],
                        'note': result[2]}]
            else:
                return None
        elif pattern_name:
            result = self.execute('''SELECT name,value,note FROM configuration 
                WHERE name GLOB :pattern_name''', {'pattern_name':pattern_name+'*'})
            config = []
            for row in result:
                config.append({'name': row[0],
                        'value': row[1],
                        'note': row[2]})
            return config
        else:
            result = self.execute('''SELECT name,value,note FROM configuration''')
            config = []
            for row in result:
                config.append({'name': row[0],
                        'value': row[1],
                        'note': row[2]})
            return config

    def getConfVal(self, name, default=None):
        """
        Return configuration value from database, 
        if not exist, return 'default'.
        """
        result = self.execute('''SELECT value FROM configuration 
                WHERE name=:name''', {'name':name})
        result = result.fetchone()
        if result:
            return result[0]
        else:
            return default

    def setConf(self, name, value, note=""):
        """
        Set (or insert) item in (to) configuration.
        """
        data = {'name':name, 'value':value, 'note':note}
        result = self.execute('''UPDATE configuration 
                SET value=:value, note=:note
                WHERE name=:name''', data)
        if not result.rowcount:
            result = self.execute('''INSERT INTO configuration
                    (name, value, note) VALUES (:name, :value, :note)''', data)
        return result

    def setConfVal(self, name, value):
        """
        Set value of item in configuration.
        """
        data = {'name':name, 'value':value}
        result = self.execute('''UPDATE configuration 
                SET value=:value WHERE name=:name''', data)
        if not result.rowcount:
            raise bdDbError("Volba '%s' pro nastavení hodnoty '%s' neexistuje." %\
                    (name, value))
        return True
            
    def delConf(self, name):
        """
        Delete configuration row.
        """
        result = self.execute('''DELETE FROM configuration 
                WHERE name=?''', name)
#        if not result.rowcount:
#            raise bdDbError("Volba '%s' pro nastavení hodnoty '%s' neexistuje." %\
#                    (name, value))
        return True
 



    def addClient(self, client):
        """
        Add client to database.
        """
        result = self.execute('''INSERT INTO clients
                (first_name, last_name, address, phone, mobile_phone1, mobile_phone2, notes) 
                VALUES (:first_name, :last_name, :address, 
                :phone, :mobile_phone1, :mobile_phone2, :notes)''', 
                client.getDict())
        client.setDbId(result.lastrowid)
        for key, value in client.preferences.iteritems():
            self.setConf(name="preference_%s-%s" %(client.getDbId(), key),
                    value=value, 
                    note="%s (%s %s)" % 
                            (key, client.first_name, client.last_name))
                    
        #TODO: services
        self.commit()

    def getClients(self):
        """
        Get clients.
        """
        result = self.execute('''SELECT id, first_name, last_name, address, 
                phone, mobile_phone1, mobile_phone2, notes FROM clients''')
        clients = []
        for row in result:
            #print "%s" % row[0]
            #print "%s" % row[1]
            #print "%s" % row[2]
            #print "%s" % row[3]
            #print "%s" % row[4]
            #print "%s" % row[5]
            #print "%s" % row[6]
            #print "%s" % row[7]
            client = bd_clients.Client(
                    db_id =         u(row[0]),
                    first_name =    u(row[1]), 
                    last_name =     u(row[2]), 
                    address =       u(row[3]),
                    phone =         u(row[4]), 
                    mobile_phone1 = u(row[5]),
                    mobile_phone2 = u(row[6]), 
                    notes =         u(row[7]))
            for pref in self.getConf(pattern_name="preference_%s-" % client.db_id):
                client.preferences[pref['name']] = pref['value']
            clients.append(client)

        return clients


















def u(x):
    return x



# vim:tabstop=4:shiftwidth=4:softtabstop=4:
# eof
