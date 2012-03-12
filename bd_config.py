#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Module for work with configuration (load and save to configuration file)

Class Config behave as singleton, it is necessary to obtain an instance
through method Config.getInstance().

VARIABLES:
  CONFIG_FILES:
    list of possible places default configuration files
    (next file overwrite previous set configuration).
    Must be set (or modified) before creating object of Config() class.

  CONFIG_SECTIONS:
    list of sections in configuration file
    Must be set (or modified) before creating object of Config() class.

FUNCTIONS:
  setConfigFiles(files):
    Function to set variable CONFIG_FILES.
    (list of configuration files)

  setConfigSections(sections):
    Function to set variable CONFIG_SECTIONS.
    (list of configuration sections)

CLASSES:
  Config():
    Class Config serves to access configuration saved in configuration file.
    Class Config can behave as singleton, see function bd_config.getConfig().
    __init__():
      Not directly called.
    loadFile(file):
      Load configuration file (append new and overwrite existing options).
    saveFile(file=False):
      Save configuration to 'file', if 'file' is not defined,
      last item in CONFIG_FILES is used.
    get(section, option, default):
      Get value of 'option' in 'section'.
      If 'value' don't exists, returns 'default'.
    getInt(section, option, default=None, translation=None):
      Get value of 'option' in 'section' converted to integer.
      If 'value' don't exists or not possible to convert, returns 'default'.
      For translate value to int is possible to use dictionary in form:
          {'ONE':1, 'TWO':2, 'THREE':3}
    more from:http://docs.python.org/library/configparser.html
    set(section, option, value):
      If the given section exists, set the given option to the specified value;
      otherwise raise NoSectionError. value is converted to str by 'str()';
      if not, TypeError is raised.



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

# list of possible places default configuration files
# (next file overwrite previous set configuration)
CONFIG_FILES = ('./benedat.conf',)
# list of sections in configuration file
CONFIG_SECTIONS = ('main',)
# variable with actual object of class Config
__config = None


def setConfigFiles(files):
    """
    Function to set variable CONFIG_FILES.
    (list of configuration files)
    """
    global CONFIG_FILES
    CONFIG_FILES = files

def setConfigSections(sections):
    """
    Function to set variable CONFIG_SECTIONS.
    (list of configuration sections)
    """
    global CONFIG_SECTIONS
    CONFIG_SECTIONS=sections

def getConfig():
    """
    Get singleton of Config.
    """
    global __config
    if not __config:
      __config=Config()
    return __config


class Config(ConfigParser.SafeConfigParser):
    """
    Class Config serves to access configuration saved in configuration file.
    Class Config can behave as singleton, see function bd_config.getConfig().
    """
    def __init__(self):
        ConfigParser.SafeConfigParser.__init__(self)

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

    def saveFile(self, file=None):
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
            return ConfigParser.SafeConfigParser.get(self, section, option)
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
            value = ConfigParser.SafeConfigParser.get(self, section, option)
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

    def set(self, section, option, value=None):
        """
        If the given section exists, set the given option to the specified value;
        otherwise raise NoSectionError. value is converted to str by 'str()';
        if not, TypeError is raised.
        """
        if not value:
            value = ""
        ConfigParser.SafeConfigParser.set(self, section, option, str(value))







# vim:tabstop=4:shiftwidth=4:softtabstop=4:
