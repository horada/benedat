#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Module with descriptions (for settings, ...).

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

eSettings = {
        #
        'eHoursLevelOS1': "OS - limit počtu hodin, nad který se počítá první snížená hodinová sazba",
        'eHoursLevelOS2': "OS - limit počtu hodin, nad který se počítá druhá snížená hodinová sazba",
        'eHoursLevelChB1': "ChB - limit počtu hodin, nad který se počítá první snížená hodinová sazba",
        'eHoursLevelChB2': "ChB - limit počtu hodin, nad který se počítá druhá snížená hodinová sazba",
        'eTransportPriceFuel': "cena za litr PHM stanovená pro výpočet příspěvku na dopravu na službu",
        'eTransportExp': "exponent do vzorce  výpočtu příspěvku na dopravu",
        'eTransportK': "konstanta do vzorce výpočtu příspěvku na dopravu",
        'eTransportEntryRate': "nástupní sazba do vzorce výpočtu příspěvku na dopravu",
        'eTransportClientPart': "podíl klienta na vypočtených nákladech cesty",
        'eTransportPriceChM': "cena za cestu Chotěboř - Modletín",
        'eDietRefreshmentCh': "Chotěboř - stanovená cena za 1 oběd uvařený v rámci aktivit Benediktu",
        'eDietRefreshmentM': "Modletín - stanovená cena za 1 oběd uvařený v rámci aktivit Benediktu",
        'eDietLunchCh': "Chotěboř - cena za oběd dovážený z restaurace",
        'eDietLunchM': "Modletín - cena za oběd dovážený z restaurace",
        'eDietBreakfastM': "Modletín - stanovená cena za odebranou snídani",
        'eDietDinnerM': "Modletín - stanovená cena za odebranou večeři",
        'eBilletChB1': "stanovená cena za 1 den ubytování (poskytnutý prostor a vybavení pro bydlení, energie, úklid, praní a drobné opravy ložního a osobního prádla a ošacení, žehlení)",
        'eBilletChB2': "stanovená cena za 1 den ubytování2 (poskytnutý prostor a vybavení pro bydlení, energie, úklid, praní a drobné opravy ložního a osobního prádla a ošacení, žehlení) - jiný způsob/kvalita ubytování - zatím nedojasněno",
        'eBilletChB3': "stanovená cena za 1 den ubytování3 (poskytnutý prostor a vybavení pro bydlení, energie, úklid, praní a drobné opravy ložního a osobního prádla a ošacení, žehlení) - jiný způsob/kvalita ubytování - zatím nedojasněno",
        'eBilletOS': "stanovená cena za 1 den ubytování (poskytnutý prostor a vybavení pro bydlení, energie, úklid, praní a drobné opravy ložního a osobního prádla a ošacení, žehlení)",
        'eSummaryCodeFixed': "Kód dokladu - stálá část",
        'eSummaryCodeVariable': "Kód dokladu - proměnná část",
        'eSummaryTill': "Pokladna",
        'eAccountOS': "",
        'eAccountOSBillet': "",
        'eAccountChB': "",
        'eAccountChBBillet': "",
        'eAccountBillet': "",
        'eAccountTransportClients': "",
        'eAccountRefreshment': "",
        'eAccountLunch': "",
        'eAccountBreakfast': "",
        'eAccountDinner': "",
        'eAccountDiet': "",
        }


teSettings = {
        'teSummaryAddress': "Adresa",
        'teSummaryInformation': "Doplňující informace",
        }




# vim:tabstop=4:shiftwidth=4:softtabstop=4:
# eof
