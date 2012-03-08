#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Helpful module for work with clients.
Data about one client:
    firstName
    lastName
    address
    phone
    mobilePhone1
    mobilePhone2
    notes
    services - default used services
    - distance



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
import bd_logging
log = bd_logging.getLogger(__name__)


class Client():
    """
    Class for representation clients.
    """
    def __init__(self, first_name=None, last_name=None, address=None, 
            phone=None, mobile_phone1=None, mobile_phone2=None, 
            notes=None, preferences=None, db_id=None):
        self.__preferences = {}
        self.setFirstName(first_name)
        self.setLastName(last_name)
        self.setAddress(address)
        self.setPhone(phone)
        self.setMobilePhone1(mobile_phone1)
        self.setMobilePhone2(mobile_phone2)
        self.setNotes(notes)
        if preferences:
            self.setPreferences(preferences)
        self.setDbId(db_id)

    def __str__(self):
        s = "Client: \n"
        s += "first_name = '%s'\n" % self.getFirstName()
        s += "last_name = '%s'\n" % self.getLastName()
        s += "address = '%s'\n" % self.getAddress()
        s += "phone = '%s'\n" % self.getPhone()
        s += "mobile_phone1 = '%s'\n" % self.getMobilePhone1()
        s += "mobile_phone2 = '%s'\n" % self.getMobilePhone2()
        s += "notes = '%s'\n" % self.getNotes()
        s += "preferences = '%s'\n" % self.getPreferences()
        s += "db_id = '%s'\n" % self.getDbId()
        return s

    def __repr__(self):
        s = "%s(" % self.__class__
        s += "first_name='%s', " % self.getFirstName()
        s += "last_name='%s', " % self.getLastName()
        s += "address='%s', " % self.getAddress()
        s += "phone='%s', " % self.getPhone()
        s += "mobile_phone1='%s', " % self.getMobilePhone1()
        s += "mobile_phone2='%s', " % self.getMobilePhone2()
        s += "notes='%s', " % self.getNotes()
        s += "preferences='%s', " % self.getPreferences()
        s += "db_id='%s')" % self.getDbId()
        return s   

    def __getitem__(self, key):
        """
        For dictionary behavior (client[first_name], ...)
        """
        return getattr(self, key)

    def getDict(self):
        """
        Return dictionary of clients informations and settings.
        """
        data = {}
        data['db_id'] = self['db_id']
        data['first_name'] = self['first_name']
        data['last_name'] = self['last_name']
        data['address'] = self['address']
        data['phone'] = self['phone']
        data['mobile_phone1'] = self['mobile_phone1']
        data['mobile_phone2'] = self['mobile_phone2']
        data['notes'] = self['notes']
#        data['preferences'] = self['preferences']
        return data

    def getFirstName(self):
        return self.__first_name
    def setFirstName(self, value):
        self.__first_name = value.strip()
    first_name = property(getFirstName, setFirstName)

    def getLastName(self):
        return self.__last_name
    def setLastName(self, value):
        self.__last_name = value.strip()
    last_name = property(getLastName, setLastName)

    def getAddress(self):
        return self.__address
    def setAddress(self, value):
        self.__address = value.strip()
    address = property(getAddress, setAddress)

    def getPhone(self):
        return self.__phone
    def setPhone(self, value):
        self.__phone = value.strip()
    phone = property(getPhone, setPhone)

    def getMobilePhone1(self):
        return self.__mobile_phone1
    def setMobilePhone1(self, value):
        self.__mobile_phone1 = value.strip()
    mobile_phone1 = property(getMobilePhone1, setMobilePhone1)

    def getMobilePhone2(self):
        return self.__mobile_phone2
    def setMobilePhone2(self, value):
        self.__mobile_phone2 = value.strip()
    mobile_phone2 = property(getMobilePhone2, setMobilePhone2)

    def getNotes(self):
        return self.__notes
    def setNotes(self, value):
        self.__notes = value.strip()
    notes = property(getNotes, setNotes)

    def getPreferences(self):
        return self.__preferences
    def setPreferences(self, value):
        self.__preferences.update(value)
#        if type(value) == dict:
#            self.__preferences = value
#        else:
#            raise ValueError("setPreferences(value=%s)"
#                    " - value must be dict not %s"%(value, type(value)))
    preferences = property(getPreferences, setPreferences)

    def setPreference(self, preference, value):
        self.__preferences[preference] = value
    def getPreference(self, preference, default_value=None):
        try:
            return self.__preferences[preference]
        except KeyError as err:
            return default_value
    def getPreferenceInt(self, preference, default_value=0):
        try:
            return int(self.__preferences[preference])
        except KeyError as err:
            log.warning("getPreferenceInt('%s', '%s') -> KeyError: %s" % \
                    (preference, default_value, err))
            return default_value
        except ValueError as err:
            log.warning("getPreferenceInt('%s', '%s') -> ValueError %s" % \
                    (preference, default_value, err))
            return default_value


    def getDbId(self):
        return self.__db_id
    def setDbId(self, value):
        self.__db_id = value
    db_id = property(getDbId, setDbId)



















# vim:tabstop=4:shiftwidth=4:softtabstop=4:
