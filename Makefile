#
# Projekt: Projekt BZSG
# Autor:   Daniel Horák
# Datum:   
# Popis:
#

NAME=benedat#nazev programu
ZIP_NAME=$(NAME).zip

PYTHON_SOUBORY=benedat.py benedat_cas.py benedat_chyby.py benedat_config.py benedat_export_Pohoda.py benedat_gui.py benedat_log.py benedat_pdf.py benedat_sestavy.py benedat_sqlite.py
GLADE_SOUBOR=benedat_gui.glade
FONTY=fonts/LinLibertine_Bd.ttf fonts/LinLibertine_BI.ttf fonts/LinLibertineC_Re.ttf fonts/LinLibertine_It.ttf fonts/LinLibertine_Re.ttf
FONTY_ADR=fonts/
JAGPDF_SOUBORY=jagpdf.py _jagpdf.pyd 
IKONA=Benedat.png Benedat.ico
TVORBA_INSTALACE_CESTA=/home/danda/programovani/Tvorba_instalace_benedat/


PROHLIZEC=gnome-open

DOCASNE_SOUBORY= *.pyc .*.db~
VIM_DOCASNE_SOUBORY=.*.swp

.PHONY: nic zip instalator clean clean-all

nic:
	echo "Nic"

# vytvoření zip archivu
zip:
	zip $(ZIP_NAME) $(PYTHON_SOUBORY) $(GLADE_SOUBOR) $(FONTY) $(IKONA) #$(JAGPDF_SOUBORY)
	
instalator:
	cp -R $(PYTHON_SOUBORY) $(GLADE_SOUBOR) $(IKONA) $(TVORBA_INSTALACE_CESTA)Benedat/benedat/
	wine /home/danda/.wine/drive_c/Program\ Files/Inno\ Setup\ 5/Compil32.exe /cc "Z:\home\danda\programovani\Tvorba_instalace_benedat\instalace_benedat.iss"

# odstranění pomocných souborů
clean:
	rm $(DOCASNE_SOUBORY) $(ZIP_NAME)

# odstranění pomocných souborů včetně dočasných souborů vimu
clean-all:
	rm $(DOCASNE_SOUBORY) $(VIM_DOCASNE_SOUBORY)

#kompilace (3x) a zobrazení
# pdf-show:
#   $(KOMPILATOR) $(KOMP_PARAM) $(NAME_TEX)
#   $(KOMPILATOR) $(KOMP_PARAM) $(NAME_TEX)
#   #$(KOMPILATOR) $(KOMP_PARAM) $(NAME_TEX)
#   $(PROHLIZEC) $(NAME_PDF)







