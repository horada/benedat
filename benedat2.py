#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Main file for BeneDat.

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


# setup logging 
import bd_logging
bd_logging.config()
log = bd_logging.getLogger(__name__)
log.debug("Start benedat2.py.")

import sys
try:
    import pygtk
    pygtk.require("2.16")
except:
    pass
try:
    import gtk
except:
    print "ERROR: Import module gtk or gtk.glade failed."
    sys.exit(1)


import os


import bd_config


def main():
    # directory with this script set as working directory
    if os.path.dirname(sys.argv[0]):
        os.chdir(os.path.dirname(sys.argv[0]))

    # load/create configuration
    conf = bd_config.getConfig()
    
    log.info("last_open_file=%s" % conf.get('main', "last_open_file", None))



#    # nastavení dalších konfiguračních voleb
#    default_konf_volby = {  'pokladna': "HP",
#                            #'kontrola_duplicity': "true",
#                            'kod_predkontace': "6023-odleh",
#                            'kod_cleneni_dph': "nonSubsume",
#                            'kod_strediska': "0011-vl.zd",
#                            'kod_cinnosti': "odl",
#                            'ico': "0000",
#                            'aplikace': "BeneDat",
#                            'poznamka_k_exportu': "Převod dat z programu BeneDat"}
#    for volba in default_konf_volby.keys():
#        if not konf.volba(volba):
#            konf[volba] = default_konf_volby[volba]

  
    
    # Run main GUI
    import bd_gui
    gui = bd_gui.WMain()
    gtk.main()

    # save configuration to file
    conf.saveFile()







if __name__ == "__main__":
    main()
    

# vim:tabstop=4:shiftwidth=4:softtabstop=4:
# eof
