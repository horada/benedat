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

import time

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
            clerk_name=None, code_fixed=None, code_variable=None, \
            output_file="summary"):
        self.start = time.time()
        self.year = year
        self.month = month
        self.clients = clients
        self.document_type = document_type
        self.date_issue = date_issue
        self.date_payment = date_payment
        self.clerk_name = clerk_name
        self.code_fixed = code_fixed
        self.code_variable = code_variable
        self.output_file = output_file

        self.summaries = []
        for client in clients:
            if self.document_type == "PPD":
                code="%s%s" % (self.code_fixed, self.code_variable),
            else:
                code=""
            self.summaries.append(ClientSummary(client=client, 
                summary_info=SummaryInfo(
                    year=self.year, 
                    month=self.month,
                    document_type=self.document_type,
                    date_issue=self.date_issue,
                    date_payment=self.date_payment,
                    clerk_name=self.clerk_name,
                    code=code,
                    )))
            if self.document_type == "PPD":
                self.increaseCode()
        # save last used variable part of summary code
        db.setConfVal("eSummaryCodeVariable", self.code_variable)


    def __str__(self):
        tmp = ""
        for summary in self.summaries:
            tmp += "==" * 30
            tmp += "\n%s\n\n" % str(summary)
        tmp += "Generated in: %0.3fs" % (time.time() - self.start)
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
    def __init__(self, client, summary_info):
        self.info = summary_info
        self.client = db.getClient(client)
        self.records = db.getRecords(client, self.info.year, self.info.month)

        self.__timeSum()
        self.__timePrice()
        self.__valuesSum()
        self.__valuesPrice()
        self.__totalPrice()
#        print "===" * 30
#        print self.records
#        print "---" * 30


    def __str__(self):
        tmp = ""
        tmp += "Typ dokladu: %s\n" % self.info.document_type
        tmp += "Datum vystavení: %s\n" % self.info.date_issue
        tmp += "Datum platby: %s\n" % self.info.date_payment
        tmp += "Vystavil: %s\n" % self.info.clerk_name
        tmp += "Client: %s %s\n" % (self.client.last_name, self.client.first_name)
        tmp += "Kód dokladu: %s\n" % (self.info.code)
        tmp += "Celkový čas: %s\n" % {key:minutesToPretty(self.time_sum[key]) for key in self.time_sum}
        tmp += "Cena (časové údaje): %s\n" % self.time_price
        tmp += "Variables sum: %s\n" % self.variables_sum
        tmp += "Cena (ostatní): %s\n" % self.variables_price
        for record in self.records:
            tmp += "%s %s %s\n" % (record.date, record.getTimeSumPretty(), record.time_records)
        tmp += "Ceny souhrn: %s\n" % self.total_prices
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
    
    def __timePrice(self):
        """
        Count price for time related records.
        """
        self.time_price = {}
        for key in self.time_sum:
            self.time_price[key] = \
                    getattr(self, "_ClientSummary__price%s" % key, \
                    lambda:0)()
    
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
    
    def __valuesPrice(self):
        """
        Count price for time related records.
        """
        self.variables_price = {}
        for key in self.variables_sum:
            self.variables_price[key] = \
                    getattr(self, "_ClientSummary__price%s" % key, \
                    lambda:0)()

    def __totalPrice(self):
        """
        Count price for particular type of service (transport, billet, diet, ...)
        and total price.
        """
        self.total_prices = {}
        self.total_prices["transport"] = \
                self.variables_price.get('TOS', 0) + \
                self.variables_price.get('TFS', 0) + \
                self.variables_price.get('TChMo', 0) + \
                self.variables_price.get('TMoCh', 0) + \
                self.variables_price.get('TSO', 0)
        self.total_prices["diet"] = \
                self.variables_price.get('DRCh', 0) + \
                self.variables_price.get('DRM', 0) + \
                self.variables_price.get('DLCh', 0) + \
                self.variables_price.get('DLM', 0) + \
                self.variables_price.get('DBM', 0) + \
                self.variables_price.get('DDM', 0) + \
                self.variables_price.get('DO', 0)
        self.total_prices["billet"] = \
                self.variables_price.get('BChB1', 0) + \
                self.variables_price.get('BChB2', 0) + \
                self.variables_price.get('BChB3', 0) + \
                self.variables_price.get('BOS', 0) + \
                self.variables_price.get('BO', 0)
        self.total_prices['total'] = self.time_price.get('OS', 0) + \
                self.time_price.get('ChB', 0) + \
                self.total_prices.get('transport', 0) + \
                self.total_prices.get('diet', 0) + \
                self.total_prices.get('billet', 0)

    def __priceOS(self):
        """
        Calculation of OS price from number of hours. 
        """
        if self.time_sum.has_key("OS"):
            hours = self.time_sum["OS"] / float(60)
            monthHoursRate = float(self.client.getPreference("eOSMonthHoursRate", 0))
            monthRate = float(self.client.getPreference("eOSMonthRate", 0))
            hoursLevelOS1 = float(db.getConfVal("eHoursLevelOS1", 0))
            hoursLevelOS2 = float(db.getConfVal("eHoursLevelOS2", 0))
            osHoursRate1 = float(self.client.getPreference("eOSHoursRate1", 0))
            osHoursRate2 = float(self.client.getPreference("eOSHoursRate2", 0))
            osHoursRate3 = float(self.client.getPreference("eOSHoursRate3", 0))

            if hours < (monthHoursRate/2):
                os_price = monthRate/2
            else:
                os_price = monthRate

            if hours > hoursLevelOS2:
                os_price += osHoursRate3 * (hours - hoursLevelOS2) + \
                        osHoursRate2 * (hoursLevelOS2 - hoursLevelOS1) + \
                        osHoursRate1 * hoursLevelOS1
            elif hours > hoursLevelOS1:
                os_price += osHoursRate2 * (hours - hoursLevelOS1) + \
                        osHoursRate1 * hoursLevelOS1
            else:
                os_price += osHoursRate1 * hours
            return round(os_price, 2)
        else:
            return None

    def __priceChB(self):
        """
        Calculation of ChB price from number of hours. 
        """
        if self.time_sum.has_key("ChB"):
            hours = self.time_sum["ChB"] / float(60)
            monthHoursRate = float(self.client.getPreference("eChBMonthHoursRate", 0))
            monthRate = float(self.client.getPreference("eChBMonthRate", 0))
            hoursLevelChB1 = float(db.getConfVal("eHoursLevelChB1", 0))
            hoursLevelChB2 = float(db.getConfVal("eHoursLevelChB2", 0))
            chBHoursRate1 = float(self.client.getPreference("eChBHoursRate1", 0))
            chBHoursRate2 = float(self.client.getPreference("eChBHoursRate2", 0))
            chBHoursRate3 = float(self.client.getPreference("eChBHoursRate3", 0))

            if hours < (monthHoursRate/2):
                chB_price = monthRate/2
            else:
                chB_price = monthRate

            if hours > hoursLevelChB2:
                chB_price += chBHoursRate3 * (hours - hoursLevelChB2) + \
                        chBHoursRate2 * (hoursLevelChB2 - hoursLevelChB1) + \
                        chBHoursRate1 * hoursLevelChB1
            elif hours > hoursLevelChB1:
                chB_price += chBHoursRate2 * (hours - hoursLevelChB1) + \
                        chBHoursRate1 * hoursLevelChB1
            else:
                chB_price += chBHoursRate1 * hours
            return round(chB_price, 2)
        else:
            return None

    def __priceTSO(self):
        """
        Calculation of price for eTransportServiceOther. 
        """
        value = float(self.variables_sum["TSO"])
        return value

    def __priceDO(self):
        """
        Calculation of price for eDietOther.
        """
        value = float(self.variables_sum["DO"])
        return value

    def __priceBO(self):
        """
        Calculation of price for eBilletOther.
        """
        value = float(self.variables_sum["BO"])
        return value

    def __priceTOS(self):
        """
        Calculation of price for chTransportOnService.
        """
        value = float(self.variables_sum["TOS"])
        price = float(self.__priceTransport())

        return value * price

    def __priceTFS(self):
        """
        Calculation of price for chTransportFromService.
        """
        value = float(self.variables_sum["TFS"])
        price = float(self.__priceTransport())
        return value * price

    def __priceTChMo(self):
        """
        Calculation of price for chTransportChMo.
        """
        value = float(self.variables_sum["TChMo"])
        price = float(db.getConfVal("eTransportPriceChM", 0))
        return value * price

    def __priceTMoCh(self):
        """
        Calculation of price for chTransportMoCh.
        """
        value = float(self.variables_sum["TMoCh"])
        price = float(db.getConfVal("eTransportPriceChM", 0))
        return value * price

    def __priceDRCh(self):
        """
        Calculation of price for chDietRefreshmentCh.
        """
        value = float(self.variables_sum["DRCh"])
        price = float(db.getConfVal("eDietRefreshmentCh", 0))
        return value * price

    def __priceDRM(self):
        """
        Calculation of price for chDietRefreshmentM.
        """
        value = float(self.variables_sum["DRM"])
        price = float(db.getConfVal("eDietRefreshmentM", 0))
        return value * price

    def __priceDLCh(self):
        """
        Calculation of price for chDietLunchCh.
        """
        value = float(self.variables_sum["DLCh"])
        price = float(db.getConfVal("eDietLunchCh", 0))
        return value * price

    def __priceDLM(self):
        """
        Calculation of price for chDietLunchM.
        """
        value = float(self.variables_sum["DLM"])
        price = float(db.getConfVal("eDietLunchM", 0))
        return value * price

    def __priceDBM(self):
        """
        Calculation of price for chDietBreakfastM.
        """
        value = float(self.variables_sum["DBM"])
        price = float(db.getConfVal("eDietBreakfastM", 0))
        return value * price

    def __priceDDM(self):
        """
        Calculation of price for chDietDinnerM.
        """
        value = float(self.variables_sum["DDM"])
        price = float(db.getConfVal("eDietDinnerM", 0))
        return value * price

    def __priceBChB1(self):
        """
        Calculation of price for chBilletChB1.
        """
        value = float(self.variables_sum["BChB1"])
        price = float(db.getConfVal("eBilletChB1", 0))
        return value * price

    def __priceBChB2(self):
        """
        Calculation of price for chBilletChB2.
        """
        value = float(self.variables_sum["BChB2"])
        price = float(db.getConfVal("eBilletChB2", 0))
        return value * price

    def __priceBChB3(self):
        """
        Calculation of price for chBilletChB3.
        """
        value = float(self.variables_sum["BChB3"])
        price = float(db.getConfVal("eBilletChB3", 0))
        return value * price

    def __priceBOS(self):
        """
        Calculation of price for chBilletOS.
        """
        value = float(self.variables_sum["BOS"])
        price = float(db.getConfVal("eBilletOS", 0))
        return value * price

    def __priceTransport(self):
        """
        Price of one trip to/from service.
        """
        priceFuel = float(db.getConfVal("eTransportPriceFuel", 0))
        exp = float(db.getConfVal("eTransportExp", 0))
        k = float(db.getConfVal("eTransportK", 0))
        entryRate = float(db.getConfVal("eTransportEntryRate", 0))
        clientPart = float(db.getConfVal("eTransportClientPart", 0))
        distance = float(self.client.getPreference("eDistance", 0))

        # rounding to higher even number
        if distance % 2:
            distance+= 1
        # price calculation
        price = entryRate + clientPart * \
            (k / 100.0 * \
            priceFuel * \
            (distance ** exp))
        # rounding price
        return round(price, 0)


class SummaryInfo():
    """
    Additional data for summary:
        year,
        month,
        document_type,
        date_issue,
        date_payment,
        clerk_name,
        code,
    """
    def __init__(self, year, month, document_type, date_issue, date_payment, clerk_name, code):
        """
        """
        self.setYear(year)
        self.setMonth(month)
        self.setDocumentType(document_type)
        self.setDateIssue(date_issue)
        self.setDatePayment(date_payment)
        self.setClerkName(clerk_name)
        self.setCode(code)

    def getYear(self):
        return self.__year
    def setYear(self, value):
        self.__year = value
    year = property(getYear, setYear)

    def getMonth(self):
        return self.__month
    def setMonth(self, value):
        self.__month = value
    month = property(getMonth, setMonth)

    def getDocumentType(self):
        return self.__document_type
    def setDocumentType(self, value):
        self.__document_type = value
    document_type = property(getDocumentType, setDocumentType)

    def getDateIssue(self):
        return self.__date_issue
    def setDateIssue(self, value):
        self.__date_issue = value
    date_issue = property(getDateIssue, setDateIssue)

    def getDatePayment(self):
        return self.__date_payment
    def setDatePayment(self, value):
        self.__date_payment = value
    date_payment = property(getDatePayment, setDatePayment)

    def getClerkName(self):
        return self.__clerk_name
    def setClerkName(self, value):
        self.__clerk_name = value
    clerk_name = property(getClerkName, setClerkName)

    def getCode(self):
        return self.__code
    def setCode(self, value):
        self.__code = value
    code = property(getCode, setCode)


# vim:tabstop=4:shiftwidth=4:softtabstop=4:
# eof
