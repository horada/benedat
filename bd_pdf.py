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

# import ReportLab related modules
import reportlab.pdfgen.canvas as pdfgencanvas
import  reportlab.lib.pagesizes as pagesizes
import reportlab.lib.units as units
from reportlab.lib.units import cm, mm
# we know some glyphs are missing, suppress warnings
import reportlab.rl_config
#reportlab.rl_config.warnOnMissingFontGlyphs = 0
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# import other Benedat related modules
import bd_logging
import bd_database

# get logger
log = bd_logging.getLogger(__name__)

# database
db = bd_database.getDb()


# Register fonts
pdfmetrics.registerFont(TTFont('LinLibertine_Bd', 'fonts/LinLibertine_Bd.ttf'))
pdfmetrics.registerFont(TTFont('LinLibertine_BI', 'fonts/LinLibertine_BI.ttf'))
pdfmetrics.registerFont(TTFont('LinLibertineC_Re', 'fonts/LinLibertineC_Re.ttf'))
pdfmetrics.registerFont(TTFont('LinLibertine_It', 'fonts/LinLibertine_It.ttf'))
pdfmetrics.registerFont(TTFont('LinLibertine_Re', 'fonts/LinLibertine_Re.ttf'))
width, height = pagesizes.A4 #keep for later






class PdfSummary():
    """
    Class for generating summary.
    """
    def __init__(self, summary):
        log.debug("PdfSummary.__init__()")
        self.summary = summary


    def createPdfSummary(self):
        """
        Create pdf summary.
        """
        log.debug("PdfSummary.createPdfSummary()")

        canvas = pdfgencanvas.Canvas("hello.pdf", pagesizes.A4, verbosity=9)

        for client_summary in self.summary.summaries:
            client_pdf = PdfClientSummary(client_summary, canvas)
            client_pdf.createPdfClientSummary()

        # metadata
        canvas.setAuthor("Daniel Horák")
        canvas.setTitle("Můj název")
        canvas.setSubject("ěščřžýáíéĚŠČŘŽÝÁÍÉ")
        canvas.setCreator("BeneDat 2 (ReportLab)")
        canvas.setKeywords("souhrn")
        #canvas.pageHasData()
        #canvas.getPageNumber()
        #print canvas.getAvailableFonts()
        #canvas.stringWidth(self, text, fontName, fontSize, encoding=None)

        # save pdf
        canvas.save()



class PdfClientSummary():
    """
    Class for generating summary for one client.
    """
    def __init__(self, summary, canvas):
        self.summary = summary
        self.c = canvas

    def createPdfClientSummary(self):
        """
        Create pdf summary for one client.
        """
        a_x = cm
        a_y = height

        self.c.setFont('LinLibertine_Bd', 14)

        # move 0,0 to top left
        self.c.translate(0,height)

        self.c.drawString(cm,-cm,"Občanské sdružení BENEDIKTUS")

        self.c.drawRightString(width-cm,-cm,"Příjmový pokladní doklad č.%s" % self.summary.code)

        # head thin frame
        self.c.setLineWidth(0.5)
        self.c.lines((
            (cm, -cm*1.3, width-cm, -cm*1.3),
            (cm, -cm*7.3, width-cm, -cm*7.3),
            (cm, -cm*1.3, cm, -cm*7.3),
            (width-cm, -cm*1.3, width-cm, -cm*7.3),
            (width/2, -cm*1.3, width/2, -cm*7.3),
            ))

        # head thick frame (from...)
        self.c.setLineWidth(2)
        self.c.lines((
            (width/2, -cm*1.3, width-cm, -cm*1.3),
            (width/2, -cm*3.3, width-cm, -cm*3.3),
            (width/2, -cm*1.3, width/2, -cm*3.3),
            (width-cm, -cm*1.3, width-cm, -cm*3.3),
            ))


        self.c.setFont('LinLibertine_Bd', 32)
        self.c.drawString(10, 150, "+ěščřžýáíé=")

        self.c.rotate(90)
        self.c.drawString(20*cm, -10*cm, "Nahnuto")
        self.c.rotate(-90)
        self.c.drawString(10*cm, 20*cm, "Nehnuto")

        self.c.drawString(10, 100, "ěščřžýáíé=a TT Font!")
        self.c.drawCentredString(units.toLength("10.5cm"), units.toLength("15cm"), "čřžýáííáýžAFS")
        self.c.drawRightString(units.toLength("20cm"), units.toLength("5cm"), "čřžýáííáýžAFS")

        # "close" page
        self.c.showPage()








# vim:tabstop=4:shiftwidth=4:softtabstop=4:
