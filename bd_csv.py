#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Module for preparing pdf.

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


import csv

import bd_logging
import bd_database

# get logger
log = bd_logging.getLogger(__name__)

# database
db = bd_database.getDb()






class CsvSummary():
    """
    Class for generating summary.
    """
    def __init__(self, summary):
        log.debug("CsvSummary.__init__()")
        self.summary = summary



    def createCsvSummary(self):
        """
        Create csv summary.
        """
        log.debug("CsvSummary.createCsvSummary()")

        f = open("%s.csv" % self.summary.output_file, "w")
        self.csv = csv.writer(f, dialect='excel', delimiter=';')

        self.csv.writerow(( \
                'Jméno',
                'Příjmení',
                'Období',
                'Kód dokladu',
                'Počet hodin OS',
                'Cena za OS',
                'Počet hodin STD',
                'Počet hodin ChB',
                'Cena za ChB',
                'Doprava na službu',
                'Doprava ze služby',
                'Doprava Ch>Mo',
                'Doprava Mo>Ch',
                'Doprava v rámci služby',
                'Doprava celkem',
                'Občerstvení Chot.',
                'Občerstvení Modl.',
                'Oběd Chot.',
                'Oběd Modl.',
                'Snídaně Modl.',
                'Večeře Modl.',
                'Jiné stravování',
                'Stravování celkem',
                'Ubytování v rámci ChB',
                'Ubytování2 v rámci ChB',
                'Ubytování3 v rámci ChB',
                'Ubytování v rámci OS',
                'Jiné ubytování',
                'Ubytování celkem'))


        for client_summary in self.summary.summaries:
            cs = client_summary
            self.csv.writerow(( \
                    # Jméno
                    cs.client.first_name,
                    # Příjmení
                    cs.client.last_name,
                    # Období
                    "%s/%s" % (cs.info.month, cs.info.year),
                    # Kód dokladu
                    cs.info.code,
                    # Počet hodin OS
                    cs.time_sum.get("OS", 0),
                    # Cena za OS
                    cs.time_price.get("OS", 0),
                    # Počet hodin STD
                    cs.time_sum.get("STD", 0),
                    # Počet hodin ChB
                    cs.time_sum.get("ChB", 0),
                    # Cena za ChB
                    cs.time_price.get("ChB", 0),
                    # Doprava na službu
                    cs.variables_sum.get("TOS", 0),
                    # Doprava ze služby
                    cs.variables_sum.get("TFS", 0),
                    # Doprava Ch>Mo
                    cs.variables_sum.get("TChMo", 0),
                    # Doprava Mo>Ch
                    cs.variables_sum.get("TMoCh", 0),
                    # Doprava v rámci služby
                    cs.variables_sum.get("TO", 0),
                    # Doprava celkem
                    cs.total_prices['transport'],
                    # Občerstvení Chot.
                    cs.variables_sum.get("DRCh", 0),
                    # Občerstvení Modl.
                    cs.variables_sum.get("DRM", 0),
                    # Oběd Chot.
                    cs.variables_sum.get("DLCh", 0),
                    # Oběd Modl.
                    cs.variables_sum.get("DLM", 0),
                    # Snídaně Modl.
                    cs.variables_sum.get("DBM", 0),
                    # Večeře Modl.
                    cs.variables_sum.get("DDM", 0),
                    # Jiné stravování
                    cs.variables_sum.get("DO", 0),
                    # Stravování celkem
                    cs.total_prices['diet'],
                    # Ubytování v rámci ChB
                    cs.variables_sum.get("BChB1", 0),
                    # Ubytování2 v rámci ChB
                    cs.variables_sum.get("BChB2", 0),
                    # Ubytování3 v rámci ChB
                    cs.variables_sum.get("BChB3", 0),
                    # Ubytování v rámci OS
                    cs.variables_sum.get("BOS", 0),
                    # Jiné ubytování
                    cs.variables_sum.get("BO", 0),
                    # Ubytování celkem
                    cs.total_prices['billet'],
                    ))
        f.close()
























# vim:tabstop=4:shiftwidth=4:softtabstop=4:
