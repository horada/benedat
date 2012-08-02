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
from bd_datetime import minutesToPretty


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

    def __init__(self, clients=None, year=None, month=None, \
            document_type=None, date_issue=None, date_payment=None, \
            clerk_name=None, code_fixed=None, code_variable=None):
        self.year = year
        self.month = month
        self.clients = clients
        self.document_type = document_type
        self.date_issue = date_issue
        self.date_payment = date_payment
        self.clerk_name = clerk_name
        self.code_fixed = code_fixed
        self.code_variable = code_variable

        self.summaries = []
        for client in clients:
            self.summaries.append(ClientSummary(client=client, 
                year=self.year, month=self.month,
                code="%s%s" % (self.code_fixed, self.code_variable)))
            self.increaseCode()
        # save last used variable part of summary code
        db.setConfVal("eSummaryCodeVariable", self.code_variable)


    def __str__(self):
        tmp = ""
        tmp += "Typ dokladu: %s\n" % self.document_type
        tmp += "Datum vystavení: %s\n" % self.date_issue
        tmp += "Datum platby: %s\n" % self.date_payment
        tmp += "Vystavil: %s\n" % self.clerk_name
        for summary in self.summaries:
            tmp += "%s\n" % str(summary)
        return tmp


    def increaseCode(self, step=1):
        """
        """
        code_len = len(self.code_variable)
        self.code_variable = ("%%0.%sd" % code_len) % \
                (int(self.code_variable) + step)



class ClientSummary():
    """
    Summary for one client.
    """
    def __init__(self, client, year=None, month=None, code=None):
        self.client = db.getClient(client)
        self.records = db.getRecords(client, year, month)
        self.code = code

        self.__timeSum()
        self.__valuesSum()
#        print "===" * 30
#        print self.records
#        print "---" * 30


    def __str__(self):
        tmp = ""
        tmp += "Client: %s %s\n" % (self.client.last_name, self.client.first_name)
        tmp += "Kód dokladu: %s\n" % (self.code)
        tmp += "Celkový čas: %s\n" % {key:minutesToPretty(self.time_sum[key]) for key in self.time_sum}
        tmp += "Variables sum: %s\n" % self.variables_sum
        for record in self.records:
            tmp += "%s %s %s\n" % (record.date, record.getTimeSumPretty(), record.time_records)
        return tmp


    def __timeSum(self):
        """
        Count total time sum.
        """
        self.time_sum = {}
        for record in self.records:
            record_time_sum = record.getTimeSum()
            for key in record_time_sum.keys():
                self.time_sum[key] = \
                        self.time_sum.get(key, 0) + \
                        record_time_sum[key]
    
    def __valuesSum(self):
        """
        Count variables sum.
        """
        self.variables_sum = {}
        for record in self.records:
            record_variables_sum = record.getVariablesSum()
            for key in record_variables_sum.keys():
                self.variables_sum[key] = \
                        self.variables_sum.get(key, 0) + \
                        record_variables_sum[key]


# vim:tabstop=4:shiftwidth=4:softtabstop=4:
# eof
