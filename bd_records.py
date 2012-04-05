#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Helpful module for work with records.
Data in one record:
    - client
    - date
    - time records
        - service type
        - from time
        - to time
    - value records
        - service type 
        - service value

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

from bd_clients import Client
from bd_datetime import Date,Time

class Record():
    """
    Class for representation record.
    """
    def __init__(self, client, date, time_records=None, value_records=None, db_id=''):
        self.__time_records = []
        self.__value_records = []
        self.setClient(client)
        self.setDate(date)
        self.setTimeRecords(time_records)
        self.setValueRecords(value_records)
        self.setDbId(db_id)

    def __str__(self):
        s = "Record(%s %s,%s, %s, %s, %s)" % \
                (self.client.first_name, self.client.last_name, self.date, \
                self.time_records, self.value_records, self.db_id)
        return s

    def __repr__(self):
        s = "%s(%s %s,%s, %s, %s, %s)" % \
                (self.__class__, self.client.first_name, self.client.last_name, \
                self.date, self.time_records, self.value_records, self.db_id)
        return s

    def __getitem__(self, key):
        """
        For dictionary behavior (record[date], ...)
        """
        return getattr(self, key)

    def getDict(self):
        """
        Return dictionary of record informations.
        """
        data = {}
        data['db_id'] = self['db_id']
        data['client_id'] = self['client']['db_id']
        data['date'] = str(self['date'])
#        data['preferences'] = self['preferences']
        return data

    def getClient(self):
        return self.__client
    def setClient(self, value):
        self.__client = value
    client = property(getClient, setClient)

    def getDate(self):
        return self.__date
    def setDate(self, value):
        if type(value) == Date:
            self.__date = value
        else:
            self.__date = Date(value)
    date = property(getDate, setDate)

    def getTimeRecords(self):
        return self.__time_records
    def setTimeRecords(self, value):
        if type(value) == TimeRecord:
            self.__time_records.append(value)
        elif type(value) == list:
            self.__time_records = value
    time_records = property(getTimeRecords, setTimeRecords)

    def addTimeRecord(self, **values):
        """
        values: - record
                - service_type,time_from,time_to
        """
        if values.has_key('record'):
            self.__time_records.append(values['record'])
        else:
            tr = TimeRecord(service_type = values['service_type'], \
                    time_from = values['time_from'], \
                    time_to = values['time_to'])
            self.__time_records.append(tr)

    def getValueRecords(self):
        return self.__value_records
    def setValueRecords(self, value):
        if type(value) == ValueRecord:
            self.__value_records.append(value)
        elif type(value) == list:
            self.__value_records = value
    value_records = property(getValueRecords, setValueRecords)

    def addValueRecord(self, **values):
        """
        values: - record
                - service_type, value
        """
        if values.has_key('record'):
            self.__value_records.append(values['record'])
        else:
            nr = ValueRecord(service_type = values['service_type'], \
                    value = values['value'])
            self.__value_records.append(nr)

    def getDbId(self):
        return self.__db_id
    def setDbId(self, value):
        self.__db_id = value
    db_id = property(getDbId, setDbId)





class TimeRecord():
    """
    Class for representation time based record.
    """
    def __init__(self, service_type, time_from, time_to, db_id=''):
        self.setServiceType(service_type)
        self.setTimeFrom(time_from)
        self.setTimeTo(time_to)
        self.setDbId(db_id)

    def __str__(self):
        s = "TimeRecord(service_type=%s, time_from=%s, time_to=%s)" % \
                (self.service_type, self.time_from, self.time_to)
        return s

    def __repr__(self):
        s = "TimeRecord(service_type=%s, time_from=%s, time_to=%s)" % \
                (self.service_type, self.time_from, self.time_to)
        return s

    def __getitem__(self, key):
        """
        For dictionary behavior...
        """
        return getattr(self, key)

    def getDict(self, id_record=''):
        """
        Return dictionary of time record informations.
        """
        data = {}
        data['db_id'] = self['db_id']
        data['id_record'] = id_record
        data['service'] = self['service_type']
        data['time_from'] = str(self['time_from'])
        data['time_to'] = str(self['time_to'])
        return data

    def getServiceType(self):
        return self.__service_type
    def setServiceType(self, value):
        self.__service_type = value
    service_type = property(getServiceType, setServiceType)

    def getTimeFrom(self):
        return self.__time_from
    def setTimeFrom(self, value):
        if type(value) == Time:
            self.__time_from = value
        else:
            self.__time_from = Time(value)
    time_from = property(getTimeFrom, setTimeFrom)

    def getTimeTo(self):
        return self.__time_to
    def setTimeTo(self, value):
        if type(value) == Time:
            self.__time_to = value
        else:
            self.__time_to = Time(value)
    time_to = property(getTimeTo, setTimeTo)

    def getDbId(self):
        return self.__db_id
    def setDbId(self, value):
        self.__db_id = value
    db_id = property(getDbId, setDbId)




class ValueRecord():
    """
    Class for representation value record.
    """
    def __init__(self, service_type, value, db_id=''):
        self.setServiceType(service_type)
        self.setValue(value)
        self.setDbId(db_id)

    def __str__(self):
        s = "ValueRecord(service_type=%s, value=%s)" % \
                (self.service_type, self.value)
        return s

    def __repr__(self):
        s = "ValueRecord(service_type=%s, value=%s)" % \
                (self.service_type, self.value)
        return s

    def __getitem__(self, key):
        """
        For dictionary behavior...
        """
        return getattr(self, key)

    def getDict(self, id_record=''):
        """
        Return dictionary of value record informations.
        """
        data = {}
        data['db_id'] = self['db_id']
        data['id_record'] = id_record
        data['service'] = self['service_type']
        data['value'] = str(self['value'])
        return data

    def getServiceType(self):
        return self.__service_type
    def setServiceType(self, value):
        self.__service_type = value
    service_type = property(getServiceType, setServiceType)

    def getValue(self):
        return self.__value
    def setValue(self, value):
        self.__value = value
    value = property(getValue, setValue)

    def getDbId(self):
        return self.__db_id
    def setDbId(self, value):
        self.__db_id = value
    db_id = property(getDbId, setDbId)









# vim:tabstop=4:shiftwidth=4:softtabstop=4:
