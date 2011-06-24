#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Helpful module for work with date and time.

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




class Date():
    """
    Class to represent and work with date.
    """
    def __init__(self, arg=None):
        # set date to today
        self.date = datetime.date.today()
        if arg:
            set(arg)

    def __str__(self):
        return self.date.strftime('%d.%m.%Y')
    
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
        arg = arg.rstrip('.')
        
        # TODO - recognise format and parse date
        
        
        




















if __name__ == '__main__':
    # unit testing 
    import unittest

    class DatePublicInterfaceTest(unittest.TestCase):
        def setUp(self):
            pass

        def test_setToday(self):
            self.assertEqual(str(Date()),
                    datetime.date.today().strftime('%d.%m.%Y'))

        def test_setInitialFullDate(self):
            d = Date('21.6.2011')
            self.assertEqual(str(d), '21.6.2011')

        def test_setInitialPartialDate(self):
            d = Date('23.')
            self.assertEqual(str(d), 
                    datetime.date.today().strftime('23.%m.%Y'))

        def test_setDateFormat_ddmmrr(self):
            d = Date()
            d.set('12.5.2011')
            self.assertEqual(str(d), '12.5.2011')
            d.set('1.6.2011')
            self.assertEqual(str(d), '1.6.2011')
            d.set('9.12.2010')
            self.assertEqual(str(d), '9.12.2010')
            d.set('2.1.1998')
            self.assertEqual(str(d), '2.1.1998')
            d.set('12.11.12')
            self.assertEqual(str(d), '12.11.2012')
            d.set('1.1.01')
            self.assertEqual(str(d), '1.1.2001')
            d.set('9/12/2010')
            self.assertEqual(str(d), '9.12.2010')
            d.set('1/1/01')
            self.assertEqual(str(d), '1.1.2001')

        def test_setDateFormat_ddmm(self):
            d = Date()
            d.set('12.5.')
            self.assertEqual(str(d), 
                    datetime.date.today().strftime('12.5.%Y'))
            d.set('12.5')
            self.assertEqual(str(d), 
                    datetime.date.today().strftime('12.5.%Y'))
            d.set('1.2')
            self.assertEqual(str(d), 
                    datetime.date.today().strftime('1.2.%Y'))
            d.set('2.1.')
            self.assertEqual(str(d), 
                    datetime.date.today().strftime('2.1.%Y'))
            d.set('2/1')
            self.assertEqual(str(d), 
                    datetime.date.today().strftime('2.1.%Y'))

        def test_setDateFormat_dd(self):
            d = Date()
            d.set('12.')
            self.assertEqual(str(d), 
                    datetime.date.today().strftime('12.%m.%Y'))
            d.set('12.')
            self.assertEqual(str(d), 
                    datetime.date.today().strftime('12.%m.%Y'))
            d.set('1.')
            self.assertEqual(str(d), 
                    datetime.date.today().strftime('1.%m.%Y'))
            d.set('2.')
            self.assertEqual(str(d), 
                    datetime.date.today().strftime('2.%m.%Y'))






    unittest.main()




