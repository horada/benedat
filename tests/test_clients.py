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
                "321321321", "123123123", "123456789", "Poznámky\n na\nvíce řádků.")
        self.assertEqual(c.first_name, "Jan")
        self.assertEqual(c.last_name, "Novák")
        self.assertEqual(c.address, "Veselá Lhota 123\nPetrovice 32132")
        self.assertEqual(c.phone, "321321321")
        self.assertEqual(c.mobile_phone1, "123123123")
        self.assertEqual(c.mobile_phone2, "123456789")
        self.assertEqual(c.notes, "Poznámky\n na\nvíce řádků.")
        self.assertEqual(c.services, None)






if __name__ == '__main__':
    # unit testing 
    
    unittest.main()





# vim:tabstop=4:shiftwidth=4:softtabstop=4:
