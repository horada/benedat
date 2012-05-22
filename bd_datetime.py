#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Helpful module for work with date and time.

VARIABLES:
    DATE_FORMAT_RE:
        Dictionary with regexp for each possible format of date.
    TIME_FORMAT_RE
        Dictionary with regexp for each possible format of time.

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
        __repr__():
            Return "bd_datetime.Date('[d]d.[m]m.[yy]yy')".
            e.g.: "bd_datetime.Date('28.11.2011')"
        set(arg):
            Function to set date from string containing one of 
            next few representation of date.
            Values that are not inserted in 'arg', 
            are used from the original value.

            possible formats:
                [d]d.[m]m.[rr]rr
                [d]d/[m]m/[rr]rr
                [d]d.[m]m[.]
                [d]d/[m]m
                [d]d[.]
                rrrr-mm-dd
  
    Time():
        Class to represent and work with time.
        __init__(arg=None):
            If arg=None, time is set to 00:00,
            else to time given via arg (see method set(arg)).
        __str__():
            Return time in format [h]h:mm.
            e.g.: '12:30', '9:00'
        __repr__():
            Return "bd_datetime.Time('hh:mm')".
            e.g.: "bd_datetime.Date(12:00)"
        set(arg):
            Function to set time from string containing one of
            next few representation of time.
            If minutes are not inserted in 'arg', 0 is used.
            
            possible formats (instead of : should be one of ":.,-"):
                [h]h:[m]m  
                [h]hmm
                [h]h[:]
        
    
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
    "rrrr-mm-dd": re.compile(r'''^\d\d\d\d-\d\d-\d\d$'''),
    "+": re.compile(r'''^\+$'''),
    "-": re.compile(r'''^\-$''')}

TIME_FORMAT_RE = {"hh:mm": re.compile(r'''^\d?\d[:.,-]\d?\d$'''),
    "hhmm": re.compile(r'''^\d?\d\d\d$'''),
    "hh": re.compile(r'''^\d?\d[:.,-]?$''')}





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

def allToIntMinutes(*values):
    """
    Convert all values to integer (in minutes).
    """
    output = []
    for value in values:
        if type(value) == Time:
            output.append(value.toMinutes())
    return output


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
        return self.get()   
    def __repr__(self):
        return "%s('%s')" % (self.__class__, self.get('dd.mm.rrrr'))


    def set(self, arg):
        """
        Function to set date from string containing one of next few 
        representation of date.
        Values that are not inserted in 'arg', are used from the initialising.
        
        possible formats:
            [d]d.[m]m.[rr]rr
            [d]d/[m]m/[rr]rr
            [d]d.[m]m[.]
            [d]d/[m]m
            [d]d[.]
            rrrr-mm-dd
        """
        # remove any dot at the end
#        arg = arg.rstrip('.')
        if type(arg) == datetime.date:
            self.date = arg

        elif DATE_FORMAT_RE["dd.mm.rrrr"].match(arg):
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

        elif DATE_FORMAT_RE["+"].match(arg):
            self.plusDays(1)

        elif DATE_FORMAT_RE["-"].match(arg):
            self.plusDays(-1)

    def get(self, format_='d.m.rrrr'):
        """
        Return date in selected format:
            'd.m.rrrr' (default)
            'dd.mm.rrrr'
            'rrrr-mm-dd'
            ''
        """
        if format_ == 'd.m.rrrr':
            return self.date.strftime('%-1d.%-1m.%Y')
        elif format_ == 'dd.mm.rrrr':
            return self.date.strftime('%d.%m.%Y')
        elif format_ == 'rrrr-mm-dd':
            return self.date.strftime('%Y-%m-%d')

    def plusDays(self, days):
        """
        """
        self.set(datetime.date.fromordinal(self.date.toordinal()+days))


class Time():
    """
    Class to represent and work with time.
    """
    def __init__(self, arg=None):
        # default time is 00:00 
        self.time = datetime.time()
        # defines if 00:00 means 24:00
        self.midnight = False
        if arg:
            self.set(arg)

    def __str__(self):
        return self.get()

    def __repr__(self):
        return "%s('%s')" % (self.__class__, self.get())

    def get(self, format_='h:mm'):
        """
        Return time in selected format:
            'h:mm' (default)
            'hh:mm'
            ''
        """
        if format_ == 'h:mm':
            return self.time.strftime('%-1H:%M') if not self.midnight else '24:00'
        elif format_ == 'hh:mm':
            return self.time.strftime('%H:%M') if not self.midnight else '24:00'

    def __add__(a, b):
        """
        Implementation of + operator. (Return number of minutes.)
        """
#        print a
#        print b
        return TimePeriod(a.toMinutes() + b.toMinutes())

    def __sub__(a, b):
        """
        Implementation of - operator. (Return number of minutes.)
        """
#        print a
#        print b
        return TimePeriod(a.toMinutes() - b.toMinutes())

    def set(self, arg):
        """
        Function to set time from string containing one of next few 
        representation of time.
        If minutes are not inserted in 'arg', 0 is used.

        possible formats (instead of : should be one of ":.,-"):
            [h]h:[m]m  
            [h]hmm
            [h]h[:]
        """
        if TIME_FORMAT_RE["hh:mm"].match(arg):
            arg = re.sub('[:.,-]', ':', arg)
            arg = map(int, arg.split(':'))
            hour = arg[0]
            minute = arg[1]
            if hour == 24 and minute == 0:
                self.midnight = True
                hour = 0
            else:
                self.midnight = False
            self.time = self.time.replace(hour=hour, minute=minute)

        elif TIME_FORMAT_RE["hhmm"].match(arg):
            arg = map(int, [arg[:-2], arg[-2:]])
            hour = arg[0]
            minute = arg[1]
            if hour == 24 and minute == 0:
                self.midnight = True
                hour = 0
            else:
                self.midnight = False
            self.time = self.time.replace(hour=hour, minute=minute)

        elif TIME_FORMAT_RE["hh"].match(arg):
            arg = re.sub('[:.,-]', ':', arg)
            arg = map(int, filter(None, arg.split(':')))
            hour = arg[0]
            if hour == 24:
                self.midnight = True
                hour = 0
            else:
                self.midnight = False
            self.time = self.time.replace(hour=hour, minute=0)

    def toMinutes(self):
        """
        Return number of minutes (int) from 00:00. 
        (0h - 24h => 0m - 1440m)
        """
        if self.midnight:
            return 24 * 60
        else:
            return int(self.time.hour * 60 + self.time.minute)

    def fromMinutes(self, value):
        """
        Set time to time from minutes from 00:00
        """
        hour = int(value)/60
        minute = value%60
        if hour == 24 and minute == 0:
            self.midnight = True
            hour = 0
        else:
            self.midnight = False
        self.time = datetime.time(hour,minute)

class TimePeriod():
    """
    Representation of time period.
    """
    def __init__(self, a=0, b=None):
        """
        Difference input in minutes.
        a - from
        b - to
        a,b type should be:
            - int => number of minutes,
            - Time
        if only a is set, then it is the difference (self.value=a)

        self.value is in minutes.
        """
        if b is None:
            b = a
            a = 0
        self.value = b - a
            

    def __str__(self):
        hours = int(self.value) / 60
        minutes = self.value % 60
        return "%d:%0.2d" % (hours, minutes)

    def __add__(a, b):
        a,b = allToIntMinutes(a,b)
        return TimePeriod(a + b)


    def __sub__(a, b):
        a,b = allToIntMinutes(a,b)
        return TimePeriod()































# vim:tabstop=4:shiftwidth=4:softtabstop=4:
