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
    - numeric records
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
    def __init__(self, client, date):
        self.setClient(client)
        self.setDate(date)

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



class TimeRecord():
    """
    Class for representation time based record.
    """
    def __init__(self, service_type, from_time, to_time):
        self.setServiceType(service_type)
        self.setFromTime(service_type)
        self.setToTime(service_type)
        
    def getServiceType(self):
        return self.__service_type
    def setServiceType(self, value):
        self.__service_type = value
    service_type = property(getServiceType, setServiceType)

    def getFromTime(self):
        return self.__from_time
    def setFromTime(self, value):
        if type(value) == Time:
            self.__from_time = value
        else:
            self.__from_time = Time(value)
    from_time = property(getFromTime, setFromTime)

    def getToTime(self):
        return self.__to_time
    def setToTime(self, value):
        if type(value) == Time:
            self.__to_time = value
        else:
            self.__to_time = Time(value)
    to_time = property(getToTime, setToTime)










# vim:tabstop=4:shiftwidth=4:softtabstop=4:
