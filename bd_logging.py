#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Module for setup logging.


VARIABLES:

FUNCTIONS:

CLASSES:

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

import logging
import re

logger = logging.getLogger('bd.logging')
logger.debug("Module '%s' loaded." % __name__)

def getLogger(name):
  """
  return logger
  """
  return logging.getLogger('bd.%s'%name)


def config(level=logging.DEBUG):
#def config(level=logging.WARNING):
  logging.basicConfig(format='%(asctime)s %(levelname)-8s %(name)-15s |%(message)s|')
  log = logging.getLogger('bd')
  log.setLevel(level)



def rnl(text):
    """
    remove new line
    Function for replacing 'new line' with space and ("foo\nbar" => "foo bar"),
    and more than one space replace with one space ("foo     bar" => "foo bar").
    """
    return re.sub(r'\s{2,}', ' ', text.replace("\n", " "))





# vim:tabstop=4:shiftwidth=4:softtabstop=4:
