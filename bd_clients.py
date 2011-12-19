#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Helpful module for work with clients.
Data about one client:
    setFirstName
    setLastName
    setAddress
    setPhone
    setMobilePhone1
    setMobilePhone2
    setNotes
    setServices - default used services



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


class Client():
    """
    Class for representation clients.
    """
    def __init__(self, first_name=None, last_name=None, address=None, 
            phone=None, mobile_phone1=None, mobile_phone2=None, 
            notes=None, services=None):
        self.setFirstName(first_name)
        self.setLastName(last_name)
        self.setAddress(address)
        self.setPhone(phone)
        self.setMobilePhone1(mobile_phone1)
        self.setMobilePhone2(mobile_phone2)
        self.setNotes(notes)
        self.setServices(services)

    def getFirstName(self):
        return self.__first_name
    def setFirstName(self, value):
        self.__first_name = value
    first_name = property(getFirstName, setFirstName)

    def getLastName(self):
        return self.__last_name
    def setLastName(self, value):
        self.__last_name = value
    last_name = property(getLastName, setLastName)

    def getAddress(self):
        return self.__address
    def setAddress(self, value):
        self.__address = value
    address = property(getAddress, setAddress)

    def getPhone(self):
        return self.__phone
    def setPhone(self, value):
        self.__phone = value
    phone = property(getPhone, setPhone)

    def getMobilePhone1(self):
        return self.__mobile_phone1
    def setMobilePhone1(self, value):
        self.__mobile_phone1 = value
    mobile_phone1 = property(getMobilePhone1, setMobilePhone1)

    def getMobilePhone2(self):
        return self.__mobile_phone2
    def setMobilePhone2(self, value):
        self.__mobile_phone2 = value
    mobile_phone2 = property(getMobilePhone2, setMobilePhone2)

    def getNotes(self):
        return self.__notes
    def setNotes(self, value):
        self.__notes = value
    notes = property(getNotes, setNotes)

    def getServices(self):
        return self.__services
    def setServices(self, value):
        self.__services = value
    services = property(getServices, setServices)

    def containsService(self, service):
        """
        Return True if client's services contains 'service'.
        """
        return service in self.__services

    def addService(self, service):
        """
        Add 'service' to services (if it still does not contain).
        """
        if not self.containsService(service):
            self.__services.append(service)

    def removeService(self, service):
        """
        Remove 'service' from services.
        """
        if self.containsService(service):
            self.__services.remove(service)


















# vim:tabstop=4:shiftwidth=4:softtabstop=4:
