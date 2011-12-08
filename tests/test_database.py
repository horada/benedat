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
import bd_database


class DatetimeFunctionsTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_createNewDb(self):
        db = bd_database.Db("/tmp/test1.db")



















if __name__ == '__main__':
    # unit testing 
    unittest.main()


# vim:tabstop=4:shiftwidth=4:softtabstop=4:
