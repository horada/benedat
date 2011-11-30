#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
Unittests for module bd_datetime.py.
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


import os
import sys
import unittest
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(
        os.path.split(os.path.abspath(sys.argv[0]))[0],'..')))
import bd_datetime


if __name__ == '__main__':
    # unit testing 

    class DatetimeFunctionsTest(unittest.TestCase):
        def setUp(self):
            pass

        def test_emendYear(self):
            self.assertEqual(bd_datetime.emendYear(2000), 2000)
            self.assertEqual(bd_datetime.emendYear(1999), 1999)
            self.assertEqual(bd_datetime.emendYear(1950), 1950)
            self.assertEqual(bd_datetime.emendYear(2010), 2010)
            self.assertEqual(bd_datetime.emendYear(00), 2000)
            self.assertEqual(bd_datetime.emendYear(49), 2049)
            self.assertEqual(bd_datetime.emendYear(50), 1950)
            self.assertEqual(bd_datetime.emendYear(99), 1999)
            self.assertEqual(bd_datetime.emendYear(11), 2011)


    class DatePublicInterfaceTest(unittest.TestCase):
        def setUp(self):
            pass

        def test_setToday(self):
            self.assertEqual(str(bd_datetime.Date()),
                    datetime.date.today().strftime('%d.%m.%Y'))

        def test_setInitialFullDate(self):
            d = bd_datetime.Date('21.6.2011')
            self.assertEqual(str(d), '21.6.2011')

        def test_setInitialPartialDate(self):
            d = bd_datetime.Date('23.')
            self.assertEqual(str(d), 
                    datetime.date.today().strftime('23.%m.%Y'))

        def test_setDateFormat_ddmmrr(self):
            d = bd_datetime.Date()
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
            d = bd_datetime.Date()
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
            d = bd_datetime.Date()
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



    class TimePublicInterfaceTest(unittest.TestCase):
        def setUp(self):
            pass

        def test_setInitialValue(self):
            self.assertEqual(str(bd_datetime.Time()), "00:00")

        def test_setInitialFullTime(self):
            t = bd_datetime.Time('9:25')
            self.assertEqual(str(t), '09:25')

        def test_setInitialPartialTime(self):
            t = bd_datetime.Time('9')
            self.assertEqual(str(t), '09:00')

        def test_setTimeFormat_hh_mm(self):
            t = bd_datetime.Time()
            t.set('9:15')
            self.assertEqual(str(t), '09:15')
            t.set('9,15')
            self.assertEqual(str(t), '09:15')
            t.set('9.15')
            self.assertEqual(str(t), '09:15')
            t.set('9-15')
            self.assertEqual(str(t), '09:15')
            t.set('14:00')
            self.assertEqual(str(t), '14:00')
            t.set('14,00')
            self.assertEqual(str(t), '14:00')
            t.set('14.00')
            self.assertEqual(str(t), '14:00')
            t.set('14-00')
            self.assertEqual(str(t), '14:00')
            t.set('14:5')
            self.assertEqual(str(t), '14:05')
            t.set('14,5')
            self.assertEqual(str(t), '14:05')
            t.set('14.5')
            self.assertEqual(str(t), '14:05')
            t.set('14-5')
            self.assertEqual(str(t), '14:05')
#            t.set('24:00')
#            self.assertEqual(str(t), '00:00')
#            t.set('12:60')
#            self.assertEqual(str(t), '00:00')

        def test_setTimeFormat_hhmm(self):
            t = bd_datetime.Time()
            t.set('915')
            self.assertEqual(str(t), '09:15')
            t.set('915')
            self.assertEqual(str(t), '09:15')
            t.set('915')
            self.assertEqual(str(t), '09:15')
            t.set('915')
            self.assertEqual(str(t), '09:15')
            t.set('1400')
            self.assertEqual(str(t), '14:00')
            t.set('1400')
            self.assertEqual(str(t), '14:00')
            t.set('1400')
            self.assertEqual(str(t), '14:00')
            t.set('1400')
            self.assertEqual(str(t), '14:00')
#            t.set('2400')
#            self.assertEqual(str(t), '00:00')
#            t.set('1260')
#            self.assertEqual(str(t), '00:00')

        def test_setTimeFormat_hh(self):
            t = bd_datetime.Time()
            t.set('12')
            self.assertEqual(str(t), '12:00')
            t.set('8')
            self.assertEqual(str(t), '08:00')
            t.set('1:')
            self.assertEqual(str(t), '01:00')




    unittest.main()



# vim:set tabstop=4:set shiftwidth=4:set softtabstop=4: 
