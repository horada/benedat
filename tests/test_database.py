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
from pprint import pprint

sys.path.insert(0, os.path.abspath(os.path.join(
        os.path.split(os.path.abspath(sys.argv[0]))[0],'..')))
import bd_database
import bd_clients
import bd_records


class DatabaseTest(unittest.TestCase):
    def setUp(self):
        pass

#    def test_createNewDb(self):
#        db = bd_database.getDb("/tmp/test.db")
#        del(db)
#        os.remove("/tmp/test.db")


    def test_setGetConf(self):
        db = bd_database.getDb("/tmp/test.db")
        db2 = bd_database.getDb()
        self.assertTrue(db is db2, "Method getDb return same object.")
#        del(db2)
#        db = bd_database.getDb("/tmp/test.db")
#        self.assertFalse(db is db2, "__del__ correctly remove object.")


    def test_addClient(self):
        db = bd_database.getDb("/tmp/test.db")

        client = bd_clients.Client(first_name="Jan", last_name="Novák", 
                address="Horní Dolní 123", phone="123234345", 
                mobile_phone1="243432445", mobile_phone2="5675676543", 
                notes="Super poznámka")
#        client = bd_clients.Client(first_name="Jan", last_name="Novak", 
#                address="Horni Dolni 123", phone="123234345", 
#                mobile_phone1="243432445", mobile_phone2="5675676543", 
#                notes="Super poznamka")
        client.preferences["aaaa"] = "AAAAA"
        client.preferences["bbbb"] = "BBBBB"
        client.preferences["cccc"] = "CCCCC"
#        db.addClient(client)
        
#        db.getClients()
        for client in db.getClients():
#            print client.getFirstName()
#            print client.getFirstName()
#            print client.getLastName()
#            print client.getAddress()
#            print client.getPhone()
#            print client.getMobilePhone1()
#            print client.getMobilePhone2()
#            print client.getNotes()
#            print client.getServices()
#            print client.getDbId()
#            print client
            pass

 
    def test_addRecord(self):
        db = bd_database.getDb("/tmp/tmp.db")

        client = bd_clients.Client(first_name="Jan", last_name="Novák", 
                address="Horní Dolní 123", phone="123234345", 
                mobile_phone1="243432445", mobile_phone2="5675676543", 
                notes="Super poznámka", db_id='1')

        record = bd_records.Record(client, "30.3.2012")

        record.addTimeRecord(record=bd_records.TimeRecord("OS", "10:00", "14:30"))
        record.addTimeRecord(record=bd_records.TimeRecord("OS", "15:00", "18:30"))

        record.addValueRecord(record=bd_records.ValueRecord("doprava_chm", "50"))
        record.addValueRecord(record=bd_records.ValueRecord("doprava_mch", "40"))


#        db.addRecord(record)

        pprint(db.getRecords())











if __name__ == '__main__':
    # unit testing 
    unittest.main()


# vim:tabstop=4:shiftwidth=4:softtabstop=4:
