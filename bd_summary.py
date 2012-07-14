#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Module for preparing summaries.

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

from pprint import pprint

from bd_exceptions import *
import bd_config
import bd_database
import bd_clients
import bd_records
import bd_logging


# get configuration
conf = bd_config.getConfig()
# get logger
log = bd_logging.getLogger(__name__)

# database
db = bd_database.getDb()


class Summary():
  """
  Data for whole summary.
  """
  def __init__(self, clients=None, year=None, month=None):
    self.year = year
    self.month = month
    self.clients = clients

    self.summaries = []
    for client in clients:
      self.summaries.append(ClientSummary(client=client, year=self.year, month=self.month))


  def __str__(self):
    tmp = ""
    for summary in self.summaries:
      tmp += "%s\n" % str(summary)
    return tmp





class ClientSummary():
  """
  Summary for one client.
  """
  def __init__(self, client, year=None, month=None):
    self.client = db.getClient(client)
    self.records = db.getRecords(client, year, month)
#    print "===" * 30
#    print self.records
#    print "---" * 30

  def __str__(self):
    tmp = ""
    tmp += "Client: %s %s\n" % (self.client.last_name, self.client.first_name)
    for record in self.records:
      tmp += "%s %s\n" % (record.date, record.time_records)
    return tmp


