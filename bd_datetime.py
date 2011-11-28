#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Helpful module for work with date and time.

VARIABLES:
  DATE_FORMAT_RE:
    Dictionary with regexp for each possible format of date.

FUNCTIONS:
  emendYear(year):
    Emend double digit year to 4 digit.
      0-49  => 2000 - 2049
      50-99 => 1950 - 1999

CLASSES:
  Date():
    Class to represent and work with date.
    __init__(arg=None):
      If arg=None, date is set to today,
      else to date given via arg (see method set(arg)).
    __str__():
      Return date in format '[d]d.[m]m.[yy]yy'.
      e.g.: '28.11.2011'
    __repr_():
      Return "bd_datetime.Date('[d]d.[m]m.[yy]yy')".
      e.g.: "bd_datetime.Date('28.11.2011')"
    set(arg):
      Function to set date from string containing one of 
      next few representation of date.
      Values that are not inserted in 'arg', are used from the original value.
      possible formats:
        d[d].m[m].[rr]rr
        d[d]/m[m]/[rr]rr
        d[d].m[m][.]
        d[d]/m[m]
        d[d][.]
        rrrr-mm-dd
    
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



import datetime
import re
from pprint import pprint


DATE_FORMAT_RE = {"dd.mm.rrrr": re.compile(r'''^\d?\d\.\d?\d\.(\d\d)?\d\d$'''),
    "dd/mm/rrrr": re.compile(r'''^\d?\d\/\d?\d\/(\d\d)?\d\d$'''),
    "dd.mm.": re.compile(r'''^\d?\d\.\d?\d\.?$'''),
    "dd/mm": re.compile(r'''^\d?\d\/\d?\d$'''),
    "dd.": re.compile(r'''^\d?\d\.?$'''),
    "rrr-mm-dd": re.compile(r'''^\d\d\d\d-\d\d-\d\d$''')}






def emendYear(year): 
    """
    Emend double digit year to 4 digit.
    0-49  => 2000 - 2049
    50-99 => 1950 - 1999
    """
    if year >= 100:
        return year
    elif year >= 50:
        return 1900 + year
    else:
        return 2000 + year



class Date():
    """
    Class to represent and work with date.
    """
    def __init__(self, arg=None):
        # set date to today
        self.date = datetime.date.today()
        # change date to date given via arg
        if arg:
            self.set(arg)

    def __str__(self):
        #return self.date.strftime('%d.%m.%Y')
        return "%d.%d.%d" % (self.date.day, self.date.month, self.date.year)
    
    def __repr__(self):
        return "%s('%s')" % (self.__class__, self.date.strftime('%d.%m.%Y'))


    def set(self, arg):
        """
        Function to set date from string containing one of next few 
        representation of date.
        Values that are not inserted in 'arg', are used from the initialising.
        
        possible formats:
            d[d].m[m].[rr]rr
            d[d]/m[m]/[rr]rr
            d[d].m[m][.]
            d[d]/m[m]
            d[d][.]
            rrrr-mm-dd
        """
        # remove any dot at the end
#        arg = arg.rstrip('.')
        
        # TODO - recognise format and parse date
        
        if DATE_FORMAT_RE["dd.mm.rrrr"].match(arg):
            arg = map(int, arg.split('.'))
            self.date = self.date.replace(year=emendYear(arg[2]),
                    month=arg[1], day=arg[0])

        elif DATE_FORMAT_RE["dd/mm/rrrr"].match(arg):
            arg = map(int, arg.split('/'))
            self.date = self.date.replace(year=emendYear(arg[2]),
                    month=arg[1], day=arg[0])

        elif DATE_FORMAT_RE["dd.mm."].match(arg):
            arg = map(int, filter(None, arg.split('.')))
            self.date = self.date.replace(month=arg[1], day=arg[0])

        elif DATE_FORMAT_RE["dd/mm"].match(arg):
            arg = map(int, arg.split('/'))
            self.date = self.date.replace(month=arg[1], day=arg[0])

        elif DATE_FORMAT_RE["dd."].match(arg):
            arg = map(int, filter(None, arg.split('.')))
            self.date = self.date.replace(day=arg[0])

        elif DATE_FORMAT_RE["rrrr-mm-dd"].match(arg):
            arg = map(int, arg.split('-'))
            self.date = self.date.replace(year=emendYear(arg[0]),
                    month=arg[1], day=arg[2])





# vim:set tabstop=4:set shiftwidth=4:set softtabstop=4: 
