#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Unittests for module bd_clients.py
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
import tempfile
sys.path.insert(0, os.path.abspath(os.path.join(
        os.path.split(os.path.abspath(sys.argv[0]))[0],'..')))
import bd_clients


class PublicInterfaceTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_createEmptyClient(self):
        c = bd_clients.Client()
        self.assertEqual(c.first_name, None)
        self.assertEqual(c.last_name, None)
        self.assertEqual(c.address, None)
        self.assertEqual(c.phone, None)
        self.assertEqual(c.mobile_phone1, None)
        self.assertEqual(c.mobile_phone2, None)
        self.assertEqual(c.notes, None)
        self.assertEqual(c.services, None)

    def test_createPanelledClient(self):
        c = bd_clients.Client("Jan", "Novák", "Veselá Lhota 123\nPetrovice 32132",
                "321321321", "123123123", "123456789", "Poznámky\n na\nvíce řádků.", ["OS", "STD"])
        self.assertEqual(c.first_name, "Jan")
        self.assertEqual(c.last_name, "Novák")
        self.assertEqual(c.address, "Veselá Lhota 123\nPetrovice 32132")
        self.assertEqual(c.phone, "321321321")
        self.assertEqual(c.mobile_phone1, "123123123")
        self.assertEqual(c.mobile_phone2, "123456789")
        self.assertEqual(c.notes, "Poznámky\n na\nvíce řádků.")
        self.assertEqual(c.services, ["OS", "STD"])


    def test_FirstName(self):
        c = bd_clients.Client()
        c.setFirstName("Jan")
        self.assertEqual(c.getFirstName(), "Jan")
        c = bd_clients.Client()
        c.first_name = "Honza"
        self.assertEqual(c.first_name, "Honza")
        c = bd_clients.Client()
        c.setFirstName("Jan")
        self.assertEqual(c.first_name, "Jan")
        c = bd_clients.Client()
        c.setFirstName("Honza")
        self.assertEqual(c.first_name, "Honza")

    def test_LastName(self):
        c = bd_clients.Client()
        c.setLastName("Novák")
        self.assertEqual(c.getLastName(), "Novák")
        c = bd_clients.Client()
        c.last_name = "Nováček"
        self.assertEqual(c.last_name, "Nováček")
        c = bd_clients.Client()
        c.setLastName("Novák")
        self.assertEqual(c.last_name, "Novák")
        c = bd_clients.Client()
        c.setLastName("Nováček")
        self.assertEqual(c.last_name, "Nováček")

    def test_Address(self):
        c = bd_clients.Client()
        c.setAddress("Veselá Lhota 123\nPetrovice 32132")
        self.assertEqual(c.getAddress(), "Veselá Lhota 123\nPetrovice 32132")
        c = bd_clients.Client()
        c.address = "Smutná Lhota 321\nPetrovice 12321"
        self.assertEqual(c.address, "Smutná Lhota 321\nPetrovice 12321")
        c = bd_clients.Client()
        c.setAddress("Veselá Lhota 123\nPetrovice 32132")
        self.assertEqual(c.address, "Veselá Lhota 123\nPetrovice 32132")
        c = bd_clients.Client()
        c.setAddress("Smutná Lhota 321\nPetrovice 12321")
        self.assertEqual(c.address, "Smutná Lhota 321\nPetrovice 12321")

    def test_Phone(self):
        c = bd_clients.Client()
        c.setPhone("321321321")
        self.assertEqual(c.getPhone(), "321321321")
        c = bd_clients.Client()
        c.phone = "111111111"
        self.assertEqual(c.phone, "111111111")
        c = bd_clients.Client()
        c.setPhone("321321321")
        self.assertEqual(c.phone, "321321321")
        c = bd_clients.Client()
        c.setPhone("111111111")
        self.assertEqual(c.phone, "111111111")

    def test_MobilePhone1(self):
        c = bd_clients.Client()
        c.setMobilePhone1("123123123")
        self.assertEqual(c.getMobilePhone1(), "123123123")
        c = bd_clients.Client()
        c.mobile_phone1 = "222222222"
        self.assertEqual(c.mobile_phone1, "222222222")
        c = bd_clients.Client()
        c.setMobilePhone1("123123123")
        self.assertEqual(c.mobile_phone1, "123123123")
        c = bd_clients.Client()
        c.setMobilePhone1("222222222")
        self.assertEqual(c.mobile_phone1, "222222222")

    def test_MobilePhone2(self):
        c = bd_clients.Client()
        c.setMobilePhone2("123456789")
        self.assertEqual(c.getMobilePhone2(), "123456789")
        c = bd_clients.Client()
        c.mobile_phone2 = "333333333"
        self.assertEqual(c.mobile_phone2, "333333333")
        c = bd_clients.Client()
        c.setMobilePhone2("123456789")
        self.assertEqual(c.mobile_phone2, "123456789")
        c = bd_clients.Client()
        c.setMobilePhone2("333333333")
        self.assertEqual(c.mobile_phone2, "333333333")

    def test_Notes(self):
        c = bd_clients.Client()
        c.setNotes("Poznámky\n na\nvíce řádků.")
        self.assertEqual(c.getNotes(), "Poznámky\n na\nvíce řádků.")
        c = bd_clients.Client()
        c.notes = "Poznámka\nna dva řádky."
        self.assertEqual(c.notes, "Poznámka\nna dva řádky.")
        c = bd_clients.Client()
        c.setNotes("Poznámky\n na\nvíce řádků.")
        self.assertEqual(c.notes, "Poznámky\n na\nvíce řádků.")
        c = bd_clients.Client()
        c.setNotes("Poznámka\nna dva řádky.")
        self.assertEqual(c.notes, "Poznámka\nna dva řádky.")

    def test_Services(self):
        c = bd_clients.Client()
        c.setServices(["OS", "STD"])
        self.assertEqual(c.getServices(), ["OS", "STD"])
        c = bd_clients.Client()
        c.services = ["OS"]
        self.assertEqual(c.services, ["OS"])
        c = bd_clients.Client()
        c.setServices(["OS", "STD"])
        self.assertEqual(c.services, ["OS", "STD"])
        c = bd_clients.Client()
        c.setServices(["OS"])
        self.assertEqual(c.services, ["OS"])
        
        c = bd_clients.Client(services=["OS", "STD"])
        self.assertTrue(c.containsService("OS"))
        self.assertTrue(c.containsService("STD"))
        self.assertFalse(c.containsService("AAA"))
        self.assertFalse(c.containsService("BBB"))

        c.addService("AAA")
        self.assertTrue(c.containsService("AAA"))
        c.removeService("AAA")
        self.assertFalse(c.containsService("AAA"))

        c.addService("AAA")
        c.addService("AAA")
        self.assertTrue(c.containsService("AAA"))
        c.removeService("AAA")
        c.removeService("AAA")
        self.assertFalse(c.containsService("AAA"))








if __name__ == '__main__':
    # unit testing 
    
    unittest.main()





# vim:tabstop=4:shiftwidth=4:softtabstop=4:
