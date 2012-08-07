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

        self.summaryTable()


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
        self.c.setLineJoin(2)
        self.c.setLineCap(2)
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

    def summaryTable(self):
        """
        Summary table.
        """
        self.__y -= 2*cm
        size = 10
        # table header 
        self.c.setFont('LinLibertine_Bd', size)
        self.c.drawString(1*cm, self.__y, "%s" % "datum")
        self.c.drawString(2.5*cm, self.__y, "%s" % "služba")
        self.c.drawString(3.5*cm, self.__y, "%s" % "od")
        self.c.drawString(4.5*cm, self.__y, "%s" % "do")
        self.c.drawString(5.5*cm, self.__y, "%s" % "celkem")

        self.__y -= size*1.2
        self.c.rotate(90)
        self.c.drawString(self.__y, -7.7*cm, "%s" % "doprava")
        self.c.drawString(self.__y,-10.7*cm, "%s" % "strava")
        self.c.drawString(self.__y, -14.7*cm, "%s" % "ubytování")
        self.c.rotate(-90)
#        self.c.drawString(14*cm, self.__y, "%s" % "snídaně")
#        self.c.drawString(16*cm, self.__y, "%s" % "večeře")
#        self.c.drawString(18*cm, self.__y, "%s" % "stravování")
        ##### -------------------------------------------
#        self.c.drawString( 8.5*cm, self.__y, "%s" % "2XX")
#        self.c.drawString( 9.5*cm, self.__y, "%s" % "3XX")
#        self.c.drawString(10.5*cm, self.__y, "%s" % "4XX")
#        self.c.drawString(11.5*cm, self.__y, "%s" % "5XX")
#        self.c.drawString(12.5*cm, self.__y, "%s" % "6XX")
#        self.c.drawString(13.5*cm, self.__y, "%s" % "7XX")
#        self.c.drawString(14.5*cm, self.__y, "%s" % "8XX")
#        self.c.drawString(15.5*cm, self.__y, "%s" % "9XX")
#        self.c.drawString(16.5*cm, self.__y, "%s" % "10XX")
#        self.c.drawString(17.5*cm, self.__y, "%s" % "11XX")
#        self.c.drawString(18.5*cm, self.__y, "%s" % "12XX")
        ##### -------------------------------------------
        # table header 2nd line
        size = 8
        self.c.setFont('LinLibertine_It', size)
        self.c.drawString(5.5*cm, self.__y, "%s" % "OS/STD/ChB")
#        self.c.drawString( 8*cm, self.__y, "%s" % "na/ze/Mo/Ch/o")
        self.c.rotate(90)
        # transport
        self.c.drawString(self.__y, -8*cm-0*(1.2*size), "na službu")
        self.c.drawString(self.__y, -8*cm-1*(1.2*size), "ze služby")
        self.c.drawString(self.__y, -8*cm-2*(1.2*size), "Ch > Mo")
        self.c.drawString(self.__y, -8*cm-3*(1.2*size), "Mo > Ch")
        self.c.drawString(self.__y, -8*cm-4*(1.2*size), "ostatní")
        # diet
        self.c.drawString(self.__y, -11*cm-0*(1.2*size), "občerstvení Ch")
        self.c.drawString(self.__y, -11*cm-1*(1.2*size), "občerstvení Mo")
        self.c.drawString(self.__y, -11*cm-2*(1.2*size), "oběd Ch")
        self.c.drawString(self.__y, -11*cm-3*(1.2*size), "oběd Mo")
        self.c.drawString(self.__y, -11*cm-4*(1.2*size), "snídaně Mo")
        self.c.drawString(self.__y, -11*cm-5*(1.2*size), "večeře Mo")
        self.c.drawString(self.__y, -11*cm-6*(1.2*size), "ostatní")
        # billet
        self.c.drawString(self.__y, -15*cm-0*(1.2*size), "ChB1")
        self.c.drawString(self.__y, -15*cm-1*(1.2*size), "ChB2")
        self.c.drawString(self.__y, -15*cm-2*(1.2*size), "ChB3")
        self.c.drawString(self.__y, -15*cm-3*(1.2*size), "OS")
        self.c.drawString(self.__y, -15*cm-4*(1.2*size), "ostatní")
        self.c.rotate(-90)

        self.__y -= size*0.5
        # table header line
        self.c.setLineJoin(2)
        self.c.setLineCap(2)
        self.c.setLineWidth(0.5)
        self.c.lines((
            (1*cm, self.__y, width-cm, self.__y),
            ))
        self.__y -= size
        # table body
        self.c.setFont('LinLibertine_Re', size)
        for record in self.summary.records:
            self.c.drawString(1*cm, self.__y, "%s" % record.date)

            # time records sum
#            self.__y += size*1.2*len(record.time_records)
            time_sum = record.getTimeSumPretty()
            self.c.drawString(5.5*cm, self.__y, "%s/%s/%s" % \
                    (pfv(time_sum.get('OS', '0')), \
                    pfv(time_sum.get('STD', '0')), \
                    pfv(time_sum.get('ChB', '0'))))

            # transport
            self.c.drawString(8*cm+0*(1.2*size)-size/2, self.__y, pbv(record.getValueRecord("TOS")))
            self.c.drawString(8*cm+1*(1.2*size)-size/2, self.__y, pbv(record.getValueRecord("TFS")))
            self.c.drawString(8*cm+2*(1.2*size)-size/2, self.__y, pbv(record.getValueRecord("TChMo")))
            self.c.drawString(8*cm+3*(1.2*size)-size/2, self.__y, pbv(record.getValueRecord("TMoCh")))
            self.c.drawString(8*cm+4*(1.2*size)-size/2, self.__y, pkcv(record.getValueRecord("TSO")))

            # diet
            self.c.drawString(11*cm+0*(1.2*size)-size/2, self.__y, pbv(record.getValueRecord('DRCh')))
            self.c.drawString(11*cm+1*(1.2*size)-size/2, self.__y, pbv(record.getValueRecord('DRM')))
            self.c.drawString(11*cm+2*(1.2*size)-size/2, self.__y, pbv(record.getValueRecord('DLCh')))
            self.c.drawString(11*cm+3*(1.2*size)-size/2, self.__y, pbv(record.getValueRecord('DLM')))
            self.c.drawString(11*cm+4*(1.2*size)-size/2, self.__y, pbv(record.getValueRecord('DBM')))
            self.c.drawString(11*cm+5*(1.2*size)-size/2, self.__y, pbv(record.getValueRecord('DDM')))
            self.c.drawString(11*cm+6*(1.2*size)-size/2, self.__y, pkcv(record.getValueRecord('DO')))

            # billet
            self.c.drawString(15*cm+0*(1.2*size)-size/2, self.__y, pbv(record.getValueRecord('BChB1')))
            self.c.drawString(15*cm+1*(1.2*size)-size/2, self.__y, pbv(record.getValueRecord('BChB2')))
            self.c.drawString(15*cm+2*(1.2*size)-size/2, self.__y, pbv(record.getValueRecord('BChB3')))
            self.c.drawString(15*cm+3*(1.2*size)-size/2, self.__y, pbv(record.getValueRecord('BOS')))
            self.c.drawString(15*cm+4*(1.2*size)-size/2, self.__y, pkcv(record.getValueRecord('BO')))

            # time records
            for time_record in record.time_records:
                self.c.drawString(2.5*cm, self.__y, "%s" % \
                        time_record.service_type)
                self.c.drawString(3.5*cm, self.__y, "%s" % \
                        time_record.time_from)
                self.c.drawString(4.5*cm, self.__y, "%s" % \
                        time_record.time_to)
                self.__y -= size*1.2
#            self.__y -= size*1.2
#            self.__y -= size*1.2*len(record.time_records)

#            self.__y -= size*1.2

def prettyBooleanValue(value):
    """
    Return boolean value in pretty format x/-.
    """
    value = int(value)
    if value:
        return 'x'
    else:
        return '-'
pbv = prettyBooleanValue

def prettyIntegerValue(value):
    """
    Return integer value in pretty format 3/-.
    """
    value = int(value)
    if value:
        return str(value)
    else:
        return '-'
piv = prettyIntegerValue

def prettyFloatValue(value):
    """
    Return float value in pretty format 3.2/-.
    """
    value = float(value)
    if value:
        return str(value)
    else:
        return '-'
pfv = prettyFloatValue

def prettyKCValue(value):
    """
    Return float value in pretty format 3.2/-.
    """
    value = float(value)
    if value:
        return "%0.2f kč" % value
    else:
        return '-'
    
pkcv = prettyKCValue

    


#    def (self):
#        """
#        """
#        log.debug("PdfClientSummary.()")


# vim:tabstop=4:shiftwidth=4:softtabstop=4:
    


#    def (self):
#        """
#        """
#        log.debug("PdfClientSummary.()")


# vim:tabstop=4:shiftwidth=4:softtabstop=4: