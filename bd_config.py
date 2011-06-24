#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Module for work with configuration (load and safe to configuration file)

Class Config behave as singleton, it is necessary to obtain an instance
through method Config.getInstance().
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


import ConfigParser
from lib.singletonmixin import Singleton

# list of possible places default configuration files
# (next file overwrite previous set configuration)
CONFIG_FILES = ('./benedat.conf',)
# list of sections in configuration file
CONFIG_SECTIONS = ('default',)


def setConfigFiles(files):
    """
    Function to set variable CONFIG_FILES.
    (list of configuration files)
    """
    global CONFIG_FILES
    CONFIG_FILES=files

def setConfigSections(sections):
    """
    Function to set variable CONFIG_SECTIONS.
    (list of configuration sections)
    """
    global CONFIG_SECTIONS
    CONFIG_SECTIONS=sections


class Config(ConfigParser.SafeConfigParser, Singleton):
    """
    Class Config serves to access configuration saved in configuration file.
    Class Config behave as singleton, it is necessary to obtain an instance 
    through method Config.getInstance().
    """
    def __init__(self):
        super(Config, self).__init__()

        # creating necessary sections
        for section in CONFIG_SECTIONS:
            self.add_section(section)

        # load default configuration files
        self.read(CONFIG_FILES)

    def loadFile(self, file):
        """
        Load configuration file (append new and overwrite existing options).
        """
        # load configuration file
        self.read(file)

    def saveFile(self, file=False):
        """
        Save configuration to 'file', if 'file' is not defined, last item of 
        CONFIG_FILES is used.
        """
        if not file:
            file = CONFIG_FILES[-1]
        # Writing our configuration file to 'file'
        with open(file, 'wb') as configfile:
            self.write(configfile)


    def get(self, section, option, default=None):
        """ 
        Get value of 'option' in 'section'. 
        If 'value' don't exists, returns 'default'. 
        """
        try :
            return super(Config, self).get(section, option)
        except ConfigParser.NoOptionError:
            # Option don't exists - return default
            return default

    def getInt(self, section, option, default=None, translation=None):
        """ 
        Get value of 'option' in 'section' converted to integer.
        If 'value' don't exists or not possible to convert, returns 'default'.
        For translate value to int is possible to use dictionary in form:
            {'ONE':1, 'TWO':2, 'THREE':3}
        """
        try :
            value = super(Config, self).get(section, option)
            return int(value)
        except ConfigParser.NoOptionError:
            # option don't exists - return default
            return default
        except ValueError:
            # option is not possible to converted to integer
            if translation is None:
                # dictionary for translate don't exists - return default
                return default
            else :
                try : 
                    # try to translate value with dictionary
                    return int(translation[value])
                except KeyError:
                    # value is not in dictionary - return default
                    return default






if __name__ == '__main__':
    # unit testing 
    import unittest
    import tempfile

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
            setConfigFiles(self.tmp_file.name)
            # sections in testing configuration file
            setConfigSections(('testing', 'testing2'))

            self.conf = Config.getInstance()


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
            tmp=Config.getInstance()
            self.assertEquals(id(self.conf), id(tmp))


        def test_saveConfigurationToFile(self):
            self.conf.set('testing', 'new_opt', 'NEW')
            self.conf.saveFile('/tmp/TESTING_CONFIGURATION.conf')

    unittest.main()



