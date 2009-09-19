#!/usr/bin/env python
#-*- coding: utf-8 -*-

"Vyjímky a chyby"



class ChybaSoubor(Exception):
    pass

class ChybaDB(Exception):
    pass

class ChybaJinaVerzeDB(Exception):
    pass

class ChybaPrazdnePole(Exception):
    pass

class ChybaRozdilneDatum(Exception):
    pass

class ChybaStejnyZaznam(Exception):
    pass
