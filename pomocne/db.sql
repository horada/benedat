CREATE TABLE klienti (
id_klienta INTEGER NOT NULL AUTOINCREMENT ,
jmeno TEXT(50) NOT NULL ,
prijmeni TEXT(50) NOT NULL ,
adresa TEXT(200) ,
telefon TEXT(50) ,
mobil1 TEXT(50) ,
mobil2 TEXT(50) ,
pozn TEXT(500) ,
os NUMERIC NOT NULL ,
oa NUMERIC NOT NULL ,
km_os INTEGER ,
PRIMARY KEY (id_klienta)
);

CREATE TABLE zaznamy_os (
id INTEGER NOT NULL AUTOINCREMENT ,
id_klienta INTEGER NOT NULL ,
datum TEXT NOT NULL ,
cas_od TEXT NOT NULL ,
cas_do TEXT NOT NULL ,
dovoz TEXT NOT NULL ,
odvoz TEXT NOT NULL ,
PRIMARY KEY (id)
);


