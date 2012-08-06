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
from pprint import pprint
import sys

from bd_exceptions import *
import bd_clients
import bd_logging
from bd_logging import rnl
import bd_records


# variable with actual object of class Db
db = None
# get logger
log = bd_logging.getLogger(__name__)


def getDb(db_file=None, new=False):
    """
    Parameters are the same as in Db.__init__().
    First call of getDb have to contain db_file, 
    in further calls db_file and new have no effect.
    """
    global db
    log.debug("getDb(db_file='%s', new='%s')"%(db_file, new))
    if not db:
        if db_file:
            log.debug("db=Db(db_file='%s', new='%s')"%(db_file, new))
            db=Db(db_file=db_file, new=new)
        else:
            log.error("Chybí cesta k databázovému souboru.")
            raise bdMissingFileError("Chybí cesta k databázovému souboru.")
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
            log.debug("Opening database '%s'." % db_file)
            self.open_database(db_file)
        else:
            log.debug("Creating new database '%s'." % db_file)
            self.create_database(db_file)
    
    def __del__(self):
        """
        Closing database on exit.
        """
        pass
#        if type(self.__dbc) == sqlite3.Connection:
#            log.debug("Closing database connection.")
#            self.__dbc.close()
 
    def execute(self, query, data=None):
        """
        Execute database query.
        """
        log.debug("Db.execute()")
        # variable for connection cursor 
        dbcc = self.__dbc.cursor()
        try:
            if data:
                log.debug(rnl("Database cursor execute(query='%s' data='%s')."%(query, data)))
                result = dbcc.execute(query, data)
            else:
                log.debug(rnl("Database cursor execute(query='%s')."%query))
                result = dbcc.execute(query)
            return result
        except sqlite3.Error as err:
            log.error(err)
            raise
    
    def commit(self):
        """
        Commit changes to database.
        """
        log.debug("Db.commit()")
        self.__dbc.commit()
    
    def create_database(self, db_file):
        """
        Create new database and insert initial data.
        """
        log.debug("Db.create_database()")
        # create database file
        try:
            self.__dbc = sqlite3.connect(db_file)
            self.__dbc.text_factory = u
        except sqlite3.OperationalError as e:
            log.error("Nemohu vytvořit soubor %s! (%s)" % (db_file, e))
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
                    date TEXT,
                    PRIMARY KEY (ID)
                    );                    
            """
            )
            # create timed records table 
            self.execute("""
                CREATE TABLE records_time(
                    id INTEGER NOT NULL,
                    id_record INTEGER NOT NULL,
                    service TEXT,
                    time_from TEXT,
                    time_to TEXT,
                    PRIMARY KEY (ID)
                    );                    
            """
            )
            # create value records table 
            self.execute("""
                CREATE TABLE records_value(
                    id INTEGER NOT NULL,
                    id_record INTEGER NOT NULL,
                    service TEXT,
                    value TEXT,
                    PRIMARY KEY (ID)
                    );                    
            """
            )
            self.commit()
        except sqlite3.Error, e:
            log.error("Problém s vytvořením databázové struktury: %s" %e)
            raise bdDbError("Problém s vytvořením databázové struktury: %s" %e)

        # insert initial data 
        try:
            self.updateConfiguration()
            self.commit()
        except sqlite3.Error, e:
            log.error("Problém s vložením výchozího nastavení: %s" %e)
            raise bdDbError("Problém s vložením výchozího nastavení: %s" %e)

    def open_database(self, db_file):
        log.debug("Db.open_database()")
        # open database file
        try:
            self.__dbc = sqlite3.connect(db_file)
            self.__dbc.text_factory = u
        except sqlite3.OperationalError as e:
            log.error("Nemohu otevřít soubor %s! (%s)" % (db_file, e))
            raise bdFileError("Nemohu otevřít soubor %s! (%s)" % (db_file, e))
        self.verification()

    def verification(self):
        """
        Db verification.
        """
        log.debug("Db.verification()")
        try: 
            log.info("db_major_version=%s" % self.getConfVal("db_major_version"))
            log.info("db_version=%s" % self.getConfVal("db_version"))
            # TODO: db verification
        except sqlite3.OperationalError as err:
            log.error(err)
            raise



    def updateConfiguration(self, update_set=INITIAL_CONFIGURATION):
        """
        Update configuration in database (insert only non exist items).
        update_set = ({'name':"NAME", 'value':"VALUE", ''note': "NOTE"}, {..},...)
        """
        log.debug("Db.updateConfiguration()")
        for item in update_set:
            # check if item is not in database
            if "DOES_NOT_CONTAIN" == \
                    self.getConfVal(item['name'], "DOES_NOT_CONTAIN"):
                # database did not contain this item => insert it
                log.debug("Inserting configuration item setConf(name='%s', value='%s', note='%s')"% \
                        (item['name'], item['value'], item['note']))
                self.setConf(item['name'], item['value'], item['note'])

    def getConf(self, name=None, pattern_name=None):
        """
        Return configuration along to name, pattern_name or whole configuration.
        """
        log.debug("Db.getConf()")
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
        log.debug("Db.getConfVal()")
        result = self.execute('''SELECT value FROM configuration 
                WHERE name=:name''', {'name':name})
        result = result.fetchone()
        if result:
            return result[0]
        else:
            return default

    def setConf(self, name, value, note="", commit=True):
        """
        Set (or insert) item in (to) configuration.
        """
        log.debug("Db.setConf()")
        data = {'name':name, 'value':value, 'note':note}
        result = self.execute('''UPDATE configuration 
                SET value=:value, note=:note
                WHERE name=:name''', data)
        if not result.rowcount:
            result = self.execute('''INSERT INTO configuration
                    (name, value, note) VALUES (:name, :value, :note)''', data)
        if commit:
            self.commit()
        return result

    def setConfVal(self, name, value, commit=True):
        """
        Set value of item in configuration.
        """
        log.debug("Db.setConfVal()")
        data = {'name':name, 'value':value}
        result = self.execute('''UPDATE configuration 
                SET value=:value WHERE name=:name''', data)
        if not result.rowcount:
            log.error("Volba '%s' pro nastavení hodnoty '%s' neexistuje." %\
                    (name, value))
            raise bdDbError("Volba '%s' pro nastavení hodnoty '%s' neexistuje." %\
                    (name, value))
        if commit:
            self.commit()
        return True
            
    def deleteConf(self, name, commit=True):
        """
        Delete configuration row.
        """
        log.debug("Db.deleteConf()")
        result = self.execute('''DELETE FROM configuration 
                WHERE name=:name''', {'name':name})
#        if not result.rowcount:
#            raise bdDbError("Volba '%s' pro nastavení hodnoty '%s' neexistuje." %\
#                    (name, value))
        if commit:
            self.commit()
        return True
 



    def addClient(self, client, commit=True):
        """
        Add client to database.
        """
        log.debug("Db.addClient()")
        log.debug(rnl("Adding client to DB: %s" % client))
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
                    
        if commit:
            self.commit()

    def updateClient(self, client, commit=True):
        """
        Update client in database.
        """
        log.debug("Db.updateClient()")
        log.debug(rnl("Updating client in DB: %s" % client))
        result = self.execute('''UPDATE clients
                SET first_name=:first_name, last_name=:last_name, address=:address,
                phone=:phone, mobile_phone1=:mobile_phone1, 
                mobile_phone2=:mobile_phone2, notes=:notes 
                WHERE id=:db_id''', 
                client.getDict())
        for key, value in client.preferences.iteritems():
            self.setConf(name="preference_%s-%s" %(client.getDbId(), key),
                    value=value, 
                    note="%s (%s %s)" % 
                            (key, client.first_name, client.last_name),
                    commit=False)
                    
        if commit:
            self.commit()



    def getClients(self):
        """
        Get clients.
        """
        log.debug("Db.getClients()")
        result = self.execute('''SELECT id, first_name, last_name, address, 
                phone, mobile_phone1, mobile_phone2, notes FROM clients''')
        clients = []
        for row in result:
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
                pref['name'] = pref['name'].split('-', 1)[1]
                client.preferences[pref['name']] = pref['value']
            clients.append(client)

        return clients

    def getClientsOfRecords(self, year=None, month=None):
        """
        Get clients with records (in given period).
        """
        log.debug("Db.getClientsOfRecords()")
        where = "WHERE clients.id=records.client"
        where_data = {}
        if year:
            if where:
                where += " AND" 
            where += " strftime('%Y', records.date)=:year"
            where_data['year'] = year
        if month:
            if where:
                where += " AND" 
            where += " strftime('%m', records.date)=:month"
            where_data['month'] = month
        result = self.execute('''SELECT clients.id, clients.first_name, 
                clients.last_name, clients.address, clients.phone, 
                clients.mobile_phone1, clients.mobile_phone2, clients.notes 
                FROM clients, records %s 
                GROUP BY clients.id''' %  \
                where, where_data)
        clients = []
        for row in result:
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
                pref['name'] = pref['name'].split('-', 1)[1]
                client.preferences[pref['name']] = pref['value']
            clients.append(client)

        return clients

    def getClientsServices(self, db_id):
        """
        Get services allowed for one client.
        """
        log.debug("Db.getClientsServices(db_id=%s)" % db_id)
        services = ('OS', 'STD', 'ChB')
        clients_services = []
        for service in services:
            if int(self.getConfVal("preference_%s-ch%s" % (db_id, service))):
                clients_services.append(service)
        return clients_services



    def getClient(self, db_id=None, name=None):
        """
        Get client.
        """
        log.debug("Db.getClient(db_id=%s, name=%s)" % (db_id, name))
        if db_id is not None:
            result = self.execute('''SELECT id, first_name, last_name, address, 
                phone, mobile_phone1, mobile_phone2, notes FROM clients
                WHERE id=:db_id''', {'db_id': str(db_id)})
        elif name is not None:
            result = self.execute('''SELECT id, first_name, last_name, address, 
                phone, mobile_phone1, mobile_phone2, notes FROM clients
                WHERE first_name||' '||last_name=:name OR 
                last_name||' '||first_name=:name''', {'name': str(name)})
        row = result.fetchone()
        if row:
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
                pref['name'] = pref['name'].split('-', 1)[1]
                client.preferences[pref['name']] = pref['value']

            return client
        return None

    def deleteClient(self, db_id, commit=True):
        """
        Delete client
        """
        log.debug("Db.deleteClient()")
        result = self.execute('''DELETE FROM clients WHERE id=:db_id''',
                {'db_id': str(db_id)})
        if commit:
            self.commit()
        return True



    def addRecord(self, record, commit=True):
        """
        Add record to database.
        """
        log.debug("Db.addRecord()")
        log.debug(rnl("Adding record to DB: %s" % record))
        result = self.execute('''INSERT INTO records
                (client, date)
                VALUES (:client_id, :date)''',
                record.getDict())
        record.setDbId(result.lastrowid)
        # insert time records
        for time_record in record.time_records:
            self.addTimeRecord(record.getDbId(), time_record, commit=False)
        # insert value records
        for value_record in record.value_records.values():
            self.addValueRecord(record.getDbId(), value_record, commit=False)
        # commit changes immediately?
        if commit:
            self.commit()

    def updateRecord(self, record, commit=True):
        """
        Update record in database.
        """
        log.debug("Db.updateRecord()")
        log.debug(rnl("Updating record in DB: %s" % record))
        result = self.execute('''UPDATE records
                SET client=:client_id, date=:date
                WHERE id=:db_id''',
                record.getDict())
        
        # update (or insert) time records
        for time_record in record.time_records:
            if time_record.getDbId():
                # update time record
                self.updateTimeRecord(record.getDbId(), time_record, commit=False)
            else:
                # insert time record
                self.addTimeRecord(record.getDbId(), time_record, commit=False)
        # update value records
        for value_record in record.value_records.values():
            self.updateValueRecord(record.getDbId(), value_record, commit=False)
        # commit changes immediately?
        if commit:
            self.commit()





    def addTimeRecord(self, id_record, time_record, commit=True):
        """
        Add time record to database.
        """
        log.debug("Db.addTimeRecord()")
        log.debug(rnl("Adding time record to DB: %s" % time_record))
        result = self.execute('''INSERT INTO records_time
                (id_record, service, time_from, time_to)
                VALUES (:id_record, :service, :time_from, :time_to)''',
                time_record.getDict(id_record=id_record))
        time_record.setDbId(result.lastrowid)
        # commit changes immediately?
        if commit:
            self.commit()

    def updateTimeRecord(self, id_record, time_record, commit=True):
        """
        Update time record in database.
        """
        log.debug("Db.updateTimeRecord()")
        log.debug(rnl("Update time record in DB: %s" % time_record))
        result = self.execute('''UPDATE records_time
                SET id_record=:id_record, service=:service, 
                time_from=:time_from, time_to=:time_to
                WHERE id=:db_id''',
                time_record.getDict(id_record=id_record))
        # commit changes immediately?
        if commit:
            self.commit()


    def addValueRecord(self, id_record, value_record, commit=True):
        """
        Add value record to database.
        """
        log.debug("Db.addValueRecord()")
        log.debug(rnl("Adding value record to DB: %s" % value_record))
        result = self.execute('''INSERT INTO records_value
                (id_record, service, value)
                VALUES (:id_record, :service, :value)''',
                value_record.getDict(id_record=id_record))
        value_record.setDbId(result.lastrowid)
        # commit changes immediately?
        if commit:
            self.commit()

    def updateValueRecord(self, id_record, value_record, commit=True):
        """
        Update value record in database.
        """
        log.debug("Db.updateValueRecord()")
        log.debug(rnl("Update value record in DB: %s" % value_record))
        result = self.execute('''UPDATE records_value
                SET value=:value
                WHERE id_record=:id_record AND service=:service''',
                value_record.getDict(id_record=id_record))
        # commit changes immediately?
        if commit:
            self.commit()

    def getRecords(self, client=None, year=None, month=None):
        """
        Get records.
        """
        log.debug("Db.getRecord()")
        records = []
        where = ''
        where_data = {}
        if client:
            if where:
                where += " AND" 
            where += " client=:client"
            where_data['client'] = client
        if year:
            if where:
                where += " AND" 
            where += " strftime('%Y', date)=:year"
            where_data['year'] = year
        if month:
            if where:
                where += " AND" 
            where += " strftime('%m', date)=:month"
            where_data['month'] = month
        if where:
            where = "WHERE %s" % where
        result = self.execute('''SELECT id, client, date FROM records %s
                ORDER BY date''' %  \
                where, where_data)
        for row in result:
            record = bd_records.Record(
                    db_id =         u(row[0]),
                    client =        self.getClient(u(row[1])),
                    date =         u(row[2]))
            # get time records
            record.setTimeRecords(self.getTimeRecords(record.db_id))
            # get value records
            record.setValueRecords(self.getValueRecords(record.db_id))
            # append record to list of records
            records.append(record)
        return records

    def getRecord(self, db_id=None):
        """
        Get record.
        """
        log.debug("Db.getRecord()")
        if db_id:
            result = self.execute('''SELECT id, client, date FROM records 
                    WHERE id=:db_id''', {'db_id':str(db_id)})
        row = result.fetchone()
        record = bd_records.Record(
                db_id =     u(row[0]),
                client =    self.getClient(u(row[1])),
                date =      u(row[2]))
        # get time records
        record.setTimeRecords(self.getTimeRecords(db_id))
        # get value records
        record.setValueRecords(self.getValueRecords(db_id))
        return record


    def getTimeRecords(self, id_record):
        """
        Get time records related to id_record.
        """
        log.debug("Db.getTimeRecords()")
        time_records = []
        result = self.execute('''SELECT id, id_record, service, time_from, time_to
                FROM records_time WHERE id_record=:id_record 
                ORDER BY time_from''', \
                {'id_record':str(id_record)})
        for row in result:
            time_record = bd_records.TimeRecord(
                    db_id =         u(row[0]),
                    service_type =  u(row[2]),
                    time_from =     u(row[3]),
                    time_to =       u(row[4]))
            time_records.append(time_record)
        return time_records

    def getValueRecords(self, id_record):
        """
        Get value records related to id_record.
        """
        log.debug("Db.getValueRecords()")
        value_records = []
        result = self.execute('''SELECT id, id_record, service, value
                FROM records_value WHERE id_record=:id_record''', \
                {'id_record':str(id_record)})
        for row in result:
            value_record = bd_records.ValueRecord(
                    db_id =         u(row[0]),
                    service_type =  u(row[2]),
                    value =         u(row[3]))
            value_records.append(value_record)
        return value_records

    def deleteRecord(self, db_id=None, commit=True):
        """
        Delete record...
        """
        log.debug("Db.deleteRecord()")
        if db_id:
            log.debug("Removing record (db_id=%s)."%db_id)
            result = self.execute('''DELETE FROM records
                    WHERE id=:db_id''', {'db_id':db_id})
            self.deleteTimeRecord(id_record=db_id, commit=False)
            self.deleteValueRecord(id_record=db_id, commit=False)
        # commit changes immediately?
        if commit:
            self.commit()

    def deleteTimeRecord(self, db_id=None, id_record=None, commit=True):
        """
        Delete time record...
        """
        log.debug("Db.deleteTimeRecord()")
        if db_id:
            log.debug("Removing time record (db_id=%s)."%db_id)
            result = self.execute('''DELETE FROM records_time
                    WHERE id=:db_id''', {'db_id':db_id})
        elif id_record:
            log.debug("Removing time record (id_record=%s)."%id_record)
            result = self.execute('''DELETE FROM records_time
                    WHERE id_record=:id_record''', {'id_record':id_record})
        # commit changes immediately?
        if commit:
            self.commit()

    def deleteValueRecord(self, db_id=None, id_record=None, service=None, \
            commit=True):
        """
        Delete value record...
        """
        log.debug("Db.deleteValueRecord()")
        if db_id:
            log.debug("Removing value record (db_id=%s)."%db_id)
            result = self.execute('''DELETE FROM records_value
                    WHERE id=:db_id''', {'db_id':db_id})
        elif id_record:
            log.debug("Removing value record (id_record=%s)."%id_record)
            result = self.execute('''DELETE FROM records_value
                    WHERE id_record=:id_record''', {'id_record':id_record})
        elif service:
            log.debug("Removing value record (service=%s)."%service)
            result = self.execute('''DELETE FROM records_value
                    WHERE service=:service''', {'service':service})
        # commit changes immediately?
        if commit:
            self.commit()


    def getRecordsYears(self):
        """
        Return list of years containing records.
        """
        log.debug("Db.getRecordsYears()")
        years = []
        result = self.execute('''SELECT strftime('%Y', date) AS year 
                FROM records GROUP BY year''')
        for row in result:
            years.append(row[0])
        return years





def u(x):
    return x



# vim:tabstop=4:shiftwidth=4:softtabstop=4:
# eof
