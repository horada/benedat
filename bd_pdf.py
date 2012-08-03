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
        log.debug("PdfClientSummary.createPdfClientSummary()")
        # move 0,0 to top left
        self.c.translate(0,height)

        # top left header
        self.topLeftHeader()
        # top right header
        self.topRightHeader()

        # head frame
        self.headFrame()

        # left address
        self.leftHeadAddress()
        # left information
        self.leftHeadInformation()

        # right address
        self.rightHeadAddress()

        # right information
        self.rightHeadInformation()




        ## EXAMPLES ##########################################################
        #self.c.setFont('LinLibertine_Bd', 32)
        #self.c.drawString(10, 150, "+ěščřžýáíé=")
        #self.c.rotate(90)
        #self.c.drawString(-10*cm, -10*cm, "Nahnuto")
        #self.c.rotate(-90)
        #self.c.drawString(10*cm, -10*cm, "Nehnuto")
        #self.c.drawString(10, -100, "ěščřžýáíé=a TT Font!")
        #self.c.drawCentredString(units.toLength("10.5cm"), units.toLength("-15cm"), "čřžýáííáýžAAAA")
        #self.c.drawRightString(units.toLength("20cm"), units.toLength("-5cm"), "čřžýáííáýžBBBB")
        ######################################################################

        # "close" page
        self.c.showPage()



    def topLeftHeader(self):
        """
        Top left header:
            "Občanské sdružení BENEDIKTUS"
        """
        log.debug("PdfClientSummary.topLeftHeader()")
        size = 14
        self.c.setFont('LinLibertine_Bd', size)
        self.c.drawString(cm,-cm,"Občanské sdružení BENEDIKTUS")

    def topRightHeader(self):
        """
        Top left header:
            "Příjmový pokladní doklad č.XXXX0000"
            "Výpis poskytnutých služeb"
        """
        log.debug("PdfClientSummary.topRightHeader()")
        if self.summary.info.document_type == "PPD":
            text = "Příjmový pokladní doklad č.%s" % self.summary.info.code
        elif self.summary.info.document_type == "JV":
            text = "Výpis poskytnutých služeb"
        size = 14
        self.c.setFont('LinLibertine_Bd', size)
        self.c.drawRightString(width-cm,-cm,text)

    def headFrame(self):
        """
        Head frame.
        """
        log.debug("PdfClientSummary.headFrame()")
        # head thin frame
        self.c.setLineWidth(0.5)
        self.c.lines((
            (cm, -cm*1.3, width-cm, -cm*1.3),
            (cm, -cm*6.0, width-cm, -cm*6.0),
            (cm, -cm*1.3, cm, -cm*6.0),
            (width-cm, -cm*1.3, width-cm, -cm*6.0),
            (width/2, -cm*1.3, width/2, -cm*6.0),
            ))
        # head thick frame (from...)
        self.c.setLineWidth(2)
        self.c.lines((
            (width/2, -cm*1.3, width-cm, -cm*1.3),
            (width/2, -cm*3.3, width-cm, -cm*3.3),
            (width/2, -cm*1.3, width/2, -cm*3.3),
            (width-cm, -cm*1.3, width-cm, -cm*3.3),
            ))


    def leftHeadAddress(self):
        """
        Left address.
        """
        log.debug("PdfClientSummary.leftHeadAddress()")
        size = 12
        # left address
        self.__y = 0
        self.c.setFont('LinLibertine_Bd', size)
        address = db.getConfVal("teSummaryAddress", "")
        for line in address.split("\n"):
            self.c.drawString(1.5*cm, -2*cm + self.__y, line)
            self.__y -= size*1.2

    def leftHeadInformation(self):
        """
        Left head information.
        """
        log.debug("PdfClientSummary.leftHeadInformation()")
        # left additional information
        size = 10
        self.c.setFont('LinLibertine_Re', size)
        information = db.getConfVal("teSummaryInformation", "")
        self.__y -= size
        for line in information.split("\n"):
            self.c.drawString(1.5*cm, -2*cm + self.__y, line)
            self.__y -= size*1.2
        

    def rightHeadAddress(self):
        """
        Right address.
        """
        log.debug("PdfClientSummary.rightHeadAddress()")
        # right name
        size = 10
        self.c.setFont('LinLibertine_Re', size)
        self.c.drawString(width/2+0.5*cm, -2*cm, "Přijato od")
        size = 14
        self.c.setFont('LinLibertine_Bd', size)
        name = "%s %s" % (self.summary.client.last_name, self.summary.client.first_name)
        self.c.drawString(width/2+0.5*cm, -2*cm - size*1.2, name)

    def rightHeadInformation(self):
        """
        Right head information.
        """
        log.debug("PdfClientSummary.rightHeadInformation()")
        # right information
        size = 12
        # descriptions
        self.c.setFont('LinLibertine_Re', size)
        if self.summary.info.document_type == "PPD":
            information = [
                    "Datum vystavení: ",
                    "Datum platby:",
                    "Pokladna:",]
        elif self.summary.info.document_type == "JV":
            information = [
                    "Datum vystavení: ",]
        self.__y = -4*cm
        for line in information:
            self.c.drawString(width/2+0.5*cm, self.__y, line)
            self.__y -= size*1.2
        # values
        self.c.setFont('LinLibertine_Bd', size)
        if self.summary.info.document_type == "PPD":
            information = [
                    self.summary.info.date_issue,
                    self.summary.info.date_payment,
                    db.getConfVal("eSummaryTill", ""),]
        elif self.summary.info.document_type == "JV":
            information = [
                    self.summary.info.date_issue,]
        self.__y = -4*cm
        for line in information:
            self.c.drawString(width/2+4.5*cm, self.__y, line)
            self.__y -= size*1.2
        # Firma není plátce DPH.
        self.c.setFont('LinLibertine_Bd', 10)
        self.c.drawString(width/2+0.5*cm, self.__y, "Firma není plátce DPH.")


#    def (self):
#        """
#        """
#        log.debug("PdfClientSummary.()")


# vim:tabstop=4:shiftwidth=4:softtabstop=4:
