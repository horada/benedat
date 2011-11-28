#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Unittests for module bd_config.py.
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
sys.path.insert(0, os.path.abspath('..'))
import bd_config



if __name__ == '__main__':
    # unit testing 

    class PublicInterfaceTest(unittest.TestCase):
        def setUp(self):
            # create temporary configuration file
            self.tmp_file = tempfile.NamedTemporaryFile(prefix='test_tmp_conf_', 
                    suffix='.conf')
            self.tmp_file.file.write('''[testing]\n'''
                                    '''opt1=Option 1\n'''
                                    '''opt2=Option 2\n'''
                                    '''# coment\n'''
                                    '''opt3=Option 3\n'''
                                    '''opt_int=12\n'''
                                    '''opt_dict=SEVEN\n'''
                                    '''\n'''
                                    '''[testing2]\n'''
                                    '''opt3=Option 3 section 2\n'''
                                    '''opt4=Option 4\n'''
                                    '''opt5=45\n'''
                                    '''\n'''
                                    '''\n'''                            
                                    '''\n''')
            self.tmp_file.file.close()
            bd_config.setConfigFiles(self.tmp_file.name)
            # sections in testing configuration file
            bd_config.setConfigSections(('testing', 'testing2'))

            self.conf = bd_config.Config.getInstance()


        def test_getExistingValues(self):
            self.assertEqual(self.conf.get('testing', 'opt1'), 'Option 1')
            self.assertEqual(self.conf.get('testing', 'opt2'), 'Option 2')
            self.assertEqual(self.conf.get('testing', 'opt3'), 'Option 3')
            self.assertEqual(self.conf.get('testing2', 'opt3'), 'Option 3 section 2')
            self.assertEqual(self.conf.get('testing2', 'opt4'), 'Option 4')
            self.assertEqual(self.conf.get('testing2', 'opt5'), '45')
        
        def test_getExistingIntegerValues(self):
            self.assertEqual(self.conf.getInt('testing', 'opt_int'), 12)
            self.assertEqual(self.conf.getInt('testing2', 'opt5'), 45)

        def test_getDefaultValues(self):
            self.assertEqual(self.conf.get('testing', 'not_exist_opt', 'DEFAULT'), 'DEFAULT')

        def test_getDefaultIntegerValues(self):
            self.assertEqual(self.conf.getInt('testing', 'not_exist_opt2', 5), 5)
            self.assertEqual(self.conf.getInt('testing', 'opt1', 7), 7)

        def test_getTranslateIntegerValues(self):
            trans_dict={'ONE':1, 'TWO':2, 'SEVEN':7}
            self.assertEqual(self.conf.getInt('testing', 'opt_dict', 7, trans_dict), 7)

        def test_setNewOption(self):
            self.conf.set('testing', 'new_opt', 'NEW')
            self.assertEqual(self.conf.get('testing', 'new_opt'), 'NEW')

        def test_returnsSameObject(self):
            tmp=bd_config.Config.getInstance()
            self.assertEquals(id(self.conf), id(tmp))


        def test_saveConfigurationToFile(self):
            self.conf.set('testing', 'new_opt', 'NEW')
            self.conf.saveFile('/tmp/TESTING_CONFIGURATION.conf')

    unittest.main()





# vim:set tabstop=4:set shiftwidth=4:set softtabstop=4: 
