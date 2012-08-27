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
from bd_datetime import minutesToPretty,minutesToHours
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


## LAYOUT CONFIGURATION VARIABLES ####################################
# table configuration variables
x_date      = 1
x_service   = 2.5
x_total     = 6
x_transport = 10
x_diet      = 13
x_billet    = 17
table_max_page_y  = 28
# summary configuration variables
x_sum_item      = 7
x_sum_total     = 12
x_sum_price     = 18
summary_max_page_y = 20
# ####################################################################



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

        canvas = pdfgencanvas.Canvas("%s.pdf" % self.summary.output_file, \
                pagesizes.A4, verbosity=9)

        for client_summary in self.summary.summaries:
            client_pdf = PdfClientSummary(client_summary, canvas)
            client_pdf.createPdfClientSummary()

        # METADATA
        # author
        canvas.setAuthor("%s - %s" % \
                (db.getConfVal("teSummaryAddress").split("\n")[0],
                self.summary.clerk_name))
        # title
        if self.summary.document_type == "PPD":
            canvas.setTitle("Příjmový pokladní doklad")
        elif self.summary.document_type == "VPS":
            canvas.setTitle("Vyúčtování poskytnutých služeb")
        else:
            canvas.setTitle("UNKNOWN")
        # subject
        canvas.setSubject("")
        canvas.setCreator("BeneDat 2")
        canvas.setKeywords("souhrn, doklad")
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

        self.__y = -6*cm
        # subject of summary above table
        self.summarySubject()

        # summary table
        self.summaryTable()

        # summary
        self.summarySummary()

        # footer
        self.footer()

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

    def anotherPage(self):
        """
        create new page (inside one client summary)
        """
        log.debug("PdfClientSummary.anotherPage()")
        size = 8
        self.c.setFont('LinLibertine_It', size)
        self.c.drawCentredString(width/2,-height+cm, \
                "pokračování na další stránce")
        self.c.showPage()
        # move 0,0 to top left
        self.c.translate(0,height)
        self.c.setFont('LinLibertine_It', size)
        self.c.drawCentredString(width/2,-cm, \
                "pokračování z předchozí stránky")
        self.__y = -1*cm

    def anotherTablePage(self):
        """
        create new page (inside one client summary)
        """
        log.debug("PdfClientSummary.anotherTablePage()")
        self.anotherPage()
        self.summaryTableHeader()

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
            "Vyúčtování poskytnutých služeb"
        """
        log.debug("PdfClientSummary.topRightHeader()")
        if self.summary.info.document_type == "PPD":
            text = "Příjmový pokladní doklad č.%s" % self.summary.info.code
        elif self.summary.info.document_type == "VPS":
            text = "Vyúčtování poskytnutých služeb"
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
        self.c.drawString(width/2+0.5*cm, -2*cm, "Přijato od  odběratele služby:")
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
                    "Datum splatnosti:",
                    "Pokladna:",]
        elif self.summary.info.document_type == "VPS":
            information = [
                    "Datum vystavení: ",
                    "Datum splatnosti:",
                    ]
        self.__y = -4*cm
        for line in information:
            self.c.drawString(width/2+0.5*cm, self.__y, line)
            self.__y -= size*1.2
        # values
        self.c.setFont('LinLibertine_Bd', size)
        if self.summary.info.document_type == "PPD":
            information = [
                    self.summary.info.date_issue,
                    self.summary.info.due_date,
                    db.getConfVal("eSummaryTill", ""),]
        elif self.summary.info.document_type == "VPS":
            information = [
                    self.summary.info.date_issue,
                    self.summary.info.due_date,
                    ]
        self.__y = -4*cm
        for line in information:
            self.c.drawString(width/2+4.5*cm, self.__y, line)
            self.__y -= size*1.2
        # Organizace není plátce DPH.
        self.c.setFont('LinLibertine_Bd', 10)
        self.c.drawString(width/2+0.5*cm, self.__y, "Organizace není plátce DPH.")

    def summarySubject(self):
        """
        Subject of summary above table.
        """
        log.debug("PdfClientSummary.summarySubject()")
        size = 12
        self.c.setFont('LinLibertine_Bd', size)
        self.c.drawString(1*cm, self.__y-(size*1.2), \
                "Účtujeme Vám za poskytnuté služby - %s/%s." % \
                (self.summary.info.month, self.summary.info.year))

    def summaryTableHeader(self):
        """
        Summary table header.
        """
        size = 10
        self.__y -= 2.0*cm
        # table header 
        self.c.setFont('LinLibertine_Bd', size)
        self.c.drawString(x_date*cm, self.__y, "%s" % "datum")
        self.c.drawString(x_service*cm, self.__y, "%s" % "služba")
        self.c.drawString(x_total*cm, self.__y, "%s" % "celkem")

        self.__y -= size*1.2
        self.c.rotate(90)
        self.c.drawString(self.__y,-x_transport*cm+1*(1.2*size), "%s" % "doprava")
        self.c.drawString(self.__y,-x_diet*cm+1*(1.2*size), "%s" % "strava")
        self.c.drawString(self.__y,-x_billet*cm+1*(1.2*size), "%s" % "ubytování")
        self.c.rotate(-90)

        # table header 2nd line
        self.c.setFont('LinLibertine_It', size)
        self.c.drawString(x_service*cm+0*cm, self.__y, "%s" % "typ")
        self.c.drawString(x_service*cm+1*cm, self.__y, "%s" % "od")
        self.c.drawString(x_service*cm+2*cm, self.__y, "%s" % "do")
        self.c.drawString(x_total*cm+0*cm, self.__y, "%s" % "OS")
        self.c.drawString(x_total*cm+1*cm, self.__y, "%s" % "STD")
        self.c.drawString(x_total*cm+2*cm, self.__y, "%s" % "ChB")
        self.c.rotate(90)
        # transport
        self.c.drawString(self.__y, -x_transport*cm-0*(1.2*size), "na službu")
        self.c.drawString(self.__y, -x_transport*cm-1*(1.2*size), "ze služby")
        self.c.drawString(self.__y, -x_transport*cm-2*(1.2*size), "Ch > Mo")
        self.c.drawString(self.__y, -x_transport*cm-3*(1.2*size), "Mo > Ch")
        self.c.drawString(self.__y, -x_transport*cm-4*(1.2*size), "ostatní")
        # diet
        self.c.drawString(self.__y, -x_diet*cm-0*(1.2*size), "občerstvení Ch")
        self.c.drawString(self.__y, -x_diet*cm-1*(1.2*size), "občerstvení Mo")
        self.c.drawString(self.__y, -x_diet*cm-2*(1.2*size), "oběd Ch")
        self.c.drawString(self.__y, -x_diet*cm-3*(1.2*size), "oběd Mo")
        self.c.drawString(self.__y, -x_diet*cm-4*(1.2*size), "snídaně Mo")
        self.c.drawString(self.__y, -x_diet*cm-5*(1.2*size), "večeře Mo")
        self.c.drawString(self.__y, -x_diet*cm-6*(1.2*size), "ostatní")
        # billet
        self.c.drawString(self.__y, -x_billet*cm-0*(1.2*size), "ChB1")
        self.c.drawString(self.__y, -x_billet*cm-1*(1.2*size), "ChB2")
        self.c.drawString(self.__y, -x_billet*cm-2*(1.2*size), "ChB3")
        self.c.drawString(self.__y, -x_billet*cm-3*(1.2*size), "OS")
        self.c.drawString(self.__y, -x_billet*cm-4*(1.2*size), "ostatní")
        self.c.rotate(-90)

        self.__y -= size*0.5
        # table header lines
        self.c.setLineJoin(2)
        self.c.setLineCap(2)
        self.c.setLineWidth(0.5)
        self.c.lines((
            (1*cm, self.__y, width-cm, self.__y),
            # 
#            (x_date*cm-2*mm-0*(1.2*size), self.__y, x_date*cm-2*mm-0*(1.2*size), self.__y+1*cm),
            (x_service*cm-2*mm-0*(1.2*size), self.__y, x_service*cm-2*mm-0*(1.2*size), self.__y+1*cm),
            (x_total*cm-3*mm, self.__y, x_total*cm-3*mm, self.__y+1*cm),
            (x_transport*cm-3*mm-1*(1.2*size), self.__y, x_transport*cm-3*mm-1*(1.2*size), self.__y+1*cm),
            (x_diet*cm-3*mm-1*(1.2*size), self.__y, x_diet*cm-3*mm-1*(1.2*size), self.__y+1*cm),
            (x_billet*cm-3*mm-1*(1.2*size), self.__y, x_billet*cm-3*mm-1*(1.2*size), self.__y+1*cm),
            ))
        self.__y -= size


    def summaryTable(self):
        """
        Summary table.
        """
        ## table head ########################
        self.summaryTableHeader()

        ## table body ########################
        size = 10
        self.c.setFont('LinLibertine_Re', size)
        for record in self.summary.records:
            # create new page?
            if self.__y-(len(record.time_records)*size*1.2) < -table_max_page_y*cm:
                # new page
                self.anotherTablePage()

            self.c.drawString(1*cm, self.__y, "%s" % record.date)

            # time records sum
#            self.__y += size*1.2*len(record.time_records)
            time_sum = record.getTimeSumPretty()
            self.c.drawString(x_total*cm+0*cm, self.__y, "%s" % \
                    pfv(time_sum.get('OS', '0')))
            self.c.drawString(x_total*cm+1*cm, self.__y, "%s" % \
                    pfv(time_sum.get('STD', '0')))
            self.c.drawString(x_total*cm+2*cm, self.__y, "%s" % \
                    pfv(time_sum.get('ChB', '0')))

            # transport
            self.c.drawString(x_transport*cm+0*(1.2*size)-size/2, self.__y, pbv(record.getValueRecord("TOS")))
            self.c.drawString(x_transport*cm+1*(1.2*size)-size/2, self.__y, pbv(record.getValueRecord("TFS")))
            self.c.drawString(x_transport*cm+2*(1.2*size)-size/2, self.__y, pbv(record.getValueRecord("TChMo")))
            self.c.drawString(x_transport*cm+3*(1.2*size)-size/2, self.__y, pbv(record.getValueRecord("TMoCh")))
            self.c.drawString(x_transport*cm+4*(1.2*size)-size/2, self.__y, pkcv(record.getValueRecord("TSO")))

            # diet
            self.c.drawString(x_diet*cm+0*(1.2*size)-size/2, self.__y, pbv(record.getValueRecord('DRCh')))
            self.c.drawString(x_diet*cm+1*(1.2*size)-size/2, self.__y, pbv(record.getValueRecord('DRM')))
            self.c.drawString(x_diet*cm+2*(1.2*size)-size/2, self.__y, pbv(record.getValueRecord('DLCh')))
            self.c.drawString(x_diet*cm+3*(1.2*size)-size/2, self.__y, pbv(record.getValueRecord('DLM')))
            self.c.drawString(x_diet*cm+4*(1.2*size)-size/2, self.__y, pbv(record.getValueRecord('DBM')))
            self.c.drawString(x_diet*cm+5*(1.2*size)-size/2, self.__y, pbv(record.getValueRecord('DDM')))
            self.c.drawString(x_diet*cm+6*(1.2*size)-size/2, self.__y, pkcv(record.getValueRecord('DO')))

            # billet
            self.c.drawString(x_billet*cm+0*(1.2*size)-size/2, self.__y, pbv(record.getValueRecord('BChB1')))
            self.c.drawString(x_billet*cm+1*(1.2*size)-size/2, self.__y, pbv(record.getValueRecord('BChB2')))
            self.c.drawString(x_billet*cm+2*(1.2*size)-size/2, self.__y, pbv(record.getValueRecord('BChB3')))
            self.c.drawString(x_billet*cm+3*(1.2*size)-size/2, self.__y, pbv(record.getValueRecord('BOS')))
            self.c.drawString(x_billet*cm+4*(1.2*size)-size/2, self.__y, pkcv(record.getValueRecord('BO')))

            # time records
            for time_record in record.time_records:
                self.c.drawString(x_service*cm+0*cm, self.__y, "%s" % \
                        time_record.service_type)
                self.c.drawString(x_service*cm+1*cm, self.__y, "%s" % \
                        time_record.time_from)
                self.c.drawString(x_service*cm+2*cm, self.__y, "%s" % \
                        time_record.time_to)
                self.__y -= size*1.2

        ## table footer ########################
        self.summaryTableFooter()

    def summaryTableFooter(self):
        """
        Summary table footer.
        """
        size = 10
        self.__y += size
        # table header lines
        self.c.setLineJoin(2)
        self.c.setLineCap(2)
        self.c.setLineWidth(0.5)
        self.c.lines((
            (1*cm, self.__y, width-cm, self.__y),
            ))
        self.__y -= size


    def summarySummary(self):
        """
        summary
        """
        log.debug("PdfClientSummary.summarySummary()")
        # create new page?
        if self.__y < -summary_max_page_y*cm:
            # new page
            pass
#            self.anotherPage()
        
        # summary header
        size = 9
        self.__y -= size * 2
        self.c.setFont('LinLibertine_Bd', size)
        self.c.drawString(x_sum_item*cm, self.__y, "položka")
        self.c.drawString(x_sum_total*cm, self.__y, "celkem")
        self.c.drawRightString(x_sum_price*cm, self.__y, "cena")
    
        # summary
        size = 10
        self.__y -= 1.2*size
        initial_y = self.__y
        # items
        self.c.setFont('LinLibertine_Re', size)
        for item in ("Odlehčovací služba", "Chráněné bydlení", \
                "Sociálně terapeutické dílny", "Doprava", "Stravování", \
                "Ubytování"):
            self.c.drawString(x_sum_item*cm, self.__y, item)
            self.__y -= 1.2*size
        self.c.setFont('LinLibertine_Bd', size)
        self.c.drawString(x_sum_item*cm, self.__y, "CELKEM")
        # total
        self.__y = initial_y
        self.c.setFont('LinLibertine_Re', size)
        self.c.drawString(x_sum_total*cm, self.__y, \
                "%s hodin" % minutesToHours(self.summary.time_sum.get('OS', 0)))
        self.__y -= 1.2*size
        self.c.drawString(x_sum_total*cm, self.__y, \
                "%s hodin" % minutesToHours(self.summary.time_sum.get('ChB', 0)))
        self.__y -= 1.2*size
        self.c.drawString(x_sum_total*cm, self.__y, \
                "%s hodin" % minutesToHours(self.summary.time_sum.get('STD', 0)))
        self.__y -= 1.2*size

        # price
        self.__y = initial_y
        self.c.setFont('LinLibertine_Re', size)
        for item in ("%s Kč" % self.summary.time_price.get('OS', 0), \
                "%s Kč" % self.summary.time_price.get('ChB', 0), \
                "-----", \
                "%s Kč" % self.summary.total_prices['transport'], \
                "%s Kč" % self.summary.total_prices['diet'], \
                "%s Kč" % self.summary.total_prices['billet']):
            self.c.drawRightString(x_sum_price*cm, self.__y, item)
            self.__y -= 1.2*size

        self.c.setFont('LinLibertine_Bd', size)
        self.c.drawRightString(x_sum_price*cm, self.__y, \
                "%s Kč" % self.summary.total_prices['total'])

        # Line
        size = 10
        self.__y -= 1.2*size
        # table header lines
        self.c.setLineJoin(2)
        self.c.setLineCap(2)
        self.c.setLineWidth(0.5)
        self.c.lines((
            (1*cm, self.__y, width-cm, self.__y),
            ))
        self.__y -= size


    def footer(self):
        """
        Page footer.
        """
        log.debug("PdfClientSummary.footer()")

        size = 12
        self.__y -= 1.5*size
        self.c.setFont('LinLibertine_Re', size)
        self.c.drawString(3*cm, self.__y, "Vystavil:")
        self.c.setFont('LinLibertine_Bd', size)
        self.c.drawString(5*cm, self.__y, self.summary.info.clerk_name)

        self.c.setFont('LinLibertine_Re', size)
        self.c.drawString(11*cm, self.__y, "Podpis odběratele:")

        self.__y -= 1.5*size
        if self.summary.info.document_type == "PPD":
            self.c.drawString(3*cm, self.__y, "Datum platby:")
            self.__y -= 1.5*size
            self.c.drawString(3*cm, self.__y, "Podpis pokladníka:")








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
        return "%0.2f Kč" % value
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
