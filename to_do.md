I faza
1. Zavrsiti dokumentaciju za fazu I
2. Videti zasto se muzika 6 tekst ne tokenizuje dobro

II faza
1. Prepraviti pravila za anotiranje u dokumentu rules.md
2. Oznaciti ponovo tekstove po dogovorenim pravilima
3. Neki tekstovi imaju greske u labelama, to treba ispraviti - kljucevi u navedenom recniku su greske
pretrazite po njima u svojim tekstovima ako ima nesto od navedenog
error_label_map = {
        'B-NAGTAG': 'O',
        'I-NAGTAG': 'O',
        'o': 'O',
        'B=ORG': 'B-ORG',
        '_   B-ORG': 'B-ORG',
        'B-ROG': 'B-ORG',
        '': 'O',
        'B=PER': 'B-PER',
        'B-period': 'B-PER',
        '_  B-LOC': 'B-LOC',
        'B-LOX': 'B-LOC',
        'И': 'O',
        'I_ORG': 'I-ORG',
        'I-ROG': 'I-ORG',
        'I-EPR': 'I-PER'
    }
4. Sve anotirane fajlove ekstenzije prebaciti u conllu - kasno sam videla da oni imaju taj nastavak
5. Anotirati fajl muzika 6
6. Treba uraditi analizu i prikaz sa graficima za sledece stvari:
    * Broj ukupnih tokena - i u njima koliko koji pripada kojoj labeli
    * Za svaki domen pojedinacno:
        - broj tokena i koliko od tih tokena pripada kojoj labeli
7. Izvestaj za 10% anotiranih tekstova
        - koliko je ukupno tokena uzeto
        - i za svaka dva anotatora procenat preklapanja/ razlike i prikaz razlika

III faza
1. Baseline model - MB (uzeti za vise razlicitih slucajeva sto se tice pretprocesiranje, pogledati ako nesto fali)
2. Trenirati bl model, potom evaluirati i ispisati
3. Classla:
    * standardni jezik
    * nestandardni jezik
4. COMtext.SR
5. SrpCNNER
6. Za svaki model ukratko napisati izvestaj:
    - tip ulaznih podataka koje model prima (ukratko opis pretprocesiranja podataka)
    - po potrebi i izlaznih podataka ako je drugacije od standardnog nesto
    - i classification report sa rezultatima evaluacije
7. Spojiti u jedan tekst i sa tabelom na kraju sa ujedinjenim prikazom, za lakse uporedjivanje reyultata dobijenih od modela

Dokumentacija
1. Sastaviti celu dokumentaciju iz svih faza u jedan fajl