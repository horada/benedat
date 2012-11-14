NAME=benedat2

APPNAME=Benedat2
VERSION=1.99.alfa
BUILD=$(shell git tag | grep "$(APPNAME)_$(VERSION)" | rev | sed 's|^\([0-9]\+\).*$$|\1|' | rev | sort -n | tail -n 1)
NEWBUILD=$(shell echo $$(($(BUILD)+1)))

ZIP_NAME=$(NAME)_$(VERSION).$(BUILD).zip

PYTHON_FILES=bd_clients.py bd_csv.py bd_datetime.py bd_exceptions.py bd_logging.py bd_records.py benedat2.py bd_config.py bd_database.py bd_descriptions.py bd_gui.py bd_pdf.py bd_summary.py
GUI_FILES=gui
GLADE_FILE=gui/bd_gui.glade
FONTS=fonts/LinLibertine_Bd.ttf fonts/LinLibertine_BI.ttf fonts/LinLibertineC_Re.ttf fonts/LinLibertine_It.ttf fonts/LinLibertine_Re.ttf
FONTS_DIR=fonts/
ICONS=gui/Benedat.png gui/Benedat.ico
MAKE_INSTALATOR_PATH=/home/dahorak/Personal/programovani/Benedat2_instalator/



TEMPORARY_FILES= *.pyc .*.db~
VIM_TEMPORARY_FILES=.*.swp

.PHONY: pass zip installer clean clean-all

pass:
	echo "Nic"
	echo "tag: $(APPNAME)_$(VERSION).$(BUILD)"

tag:
	git tag "$(APPNAME)_$(VERSION).$(NEWBUILD)"

# vytvoření zip archivu
zip:
	zip $(ZIP_NAME) $(PYTHON_FILES) $(GLADE_FILE) $(FONTS) $(ICONS)
	
installer:
	cp -R $(PYTHON_FILES) $(GUI_FILES) $(FONTS_DIR) $(MAKE_INSTALATOR_PATH)Benedat2/benedat/
	./installer.sh $(APPNAME) $(VERSION) $(BUILD)
#   wine /home/dahorak/.wine/drive_c/InnoSetup5/Compil32.exe /cc "H:\Personal\programovani\Benedat2_instalator\Benedat2_instalator.iss"

# odstranění pomocných souborů
clean:
	rm $(TEMPORARY_FILES) $(ZIP_NAME)

# odstranění pomocných souborů včetně dočasných souborů vimu
clean-all:
	rm $(TEMPORARY_FILES) $(VIM_TEMPORARY_FILES)







