#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
Unittests for module bd_database.py.
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

sys.path.insert(0, os.path.abspath(os.path.join(
        os.path.split(os.path.abspath(sys.argv[0]))[0],'..')))
import bd_records
import bd_clients


class RecordsTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_createEmptyRecord(self):
        client1 = bd_clients.Client("Jan", "Novák")
        record1 = bd_records.Record(client1, '26.3.2012')
        record2 = bd_records.Record(client1, '28.3')
        print record1
        print record2

    def test_fillRecord(self):
        client1 = bd_clients.Client("Jan", "Novák")

        record1 = bd_records.Record(client1, '26.3.2012')
        record1.addTimeRecord(service_type="OS", from_time="8:00", to_time="13:15")
#        record1.addTimeRecord(service_type="STD", from_time="9,30", to_time="1700")
        record1.addTimeRecord(service_type="ChB", from_time="8", to_time="14")
        record1.addValueRecord(service_type="TEST1", value="43")
        print record1

#        tr = bd_records.TimeRecord(











if __name__ == '__main__':
    # unit testing 
    unittest.main()


# vim:tabstop=4:shiftwidth=4:softtabstop=4:
