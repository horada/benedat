#
# Projekt: Nápověda k programu BeneDat
# Autor:   Daniel Horák
# Datum:   
# Popis:
#

NAME=Help#nazev programu
NAME_TEX=$(NAME).tex
NAME_PDF=$(NAME).pdf

KOMPILATOR=pdfcslatex # 
KOMP_PARAM=#-interaction nonstopmode #parametry kompilátoru (procházet až do konce - nezastavovat na chybách - kvuli vimu)
PROHLIZEC=gnome-open
# písmena před která se má dávat ~ (nezlomitelná mezera) - pro program vlna
PISMENA=KkSsVvZzOoUuAaIi

POMOCNE_SOUBORY= *.log *.aux *.bbl *.blg


.PHONY: pdf show pdf-show vlna

#kompilace (3x) a zobrazení
pdf-show:
	$(KOMPILATOR) $(KOMP_PARAM) $(NAME_TEX)
	$(KOMPILATOR) $(KOMP_PARAM) $(NAME_TEX)
	#$(KOMPILATOR) $(KOMP_PARAM) $(NAME_TEX)
	$(PROHLIZEC) $(NAME_PDF)

prezentace:
	$(KOMPILATOR) $(KOMP_PARAM) $(PREZENTACE_TEX)
	$(KOMPILATOR) $(KOMP_PARAM) $(PREZENTACE_TEX)
	#$(KOMPILATOR) $(KOMP_PARAM) $(PREZENTACE_TEX)
	$(PROHLIZEC) $(PREZENTACE_PDF)


# vytvoření pdf souboru (3x kompilace)
pdf:
	$(KOMPILATOR) $(NAME_TEX)
	$(KOMPILATOR) $(NAME_TEX)
	$(KOMPILATOR) $(NAME_TEX)


show:
	$(PROHLIZEC) $(NAME_PDF)

# zpracování BibTeXové databáze
bibtex:
	bibtex $(NAME)
	#bibtex bu1
	#bibtex bu2
	#bibtex bu3

# vložení nezlomitelných mezer (~)
vlna:
	vlna -l -m -n -v $(PISMENA) $(NAME_TEX)


# odstranění pomocných souborů
clean:
	rm $(POMOCNE_SOUBORY)




