# Weightlifting Germany Server [![Build Status](https://travis-ci.org/WGierke/weightlifting_germany_server.svg?branch=master)](https://travis-ci.org/WGierke/weightlifting_germany_server)

The server fetches the Bundesliga competition data and news of known German weightlifting clubs to upload them to a Google Appspot server instance.
It then notifys the Android app users of the changes via GCM.

## Planned Features
- [ ] Support push notifications for iOS app  
- [ ] Fetch news from biggest weightlifting clubs
    - [X] BVDG (TopNews)
    - [ ] AC Germania St.Ilgen (website under construction)
    - [ ] [AC Meißen](http://www.ac-meissen.de/index.php?start=1)
    - [X] [AC Mutterstadt](http://www.ac-mutterstadt.de/index.php?start=1)
    - [ ] Athletenteam Vogtland [AC Atlas Plauen](https://acatlas.wordpress.com/)
    - [X] AV Speyer 03
    - [ ] Berliner TSC (no specific weightlifting news)
    - [ ] [Chemnitzer AC](http://chemnitzer-athletenclub.de/aktuelles/news/page/1/)
    - [ ] [KSV Durlach](http://ksvdurlach.de/news?page_n54=1)
    - [X] Oder-Sund-Team
    - [ ] SG Fortschritt Eibau (no specific weightlifting news)
    - [ ] SSV Samswegen (no specific weightlifting news)
    - [ ] SV Germania Obrigheim (no news about 1. Bundesliga)
    - [X] [TB 03 Roding](http://www.tb03-gewichtheben.de/page/1/)
    - [ ] [TSV Heinsheim](http://gewichtheben.tsv-heinsheim.de/index.php?start=1)


## Current News

| Blog Name   | Heading                                                                                                                                                 | Date       | Image                                                                                                                    | Content                 |
|:------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------|:-------------------------------------------------------------------------------------------------------------------------|:------------------------|
| Speyer      | [Sportlerin, Sportler, Mannschaft des Jahres – Stadt Speyer](http://www.av03-speyer.de/2018/01/sportlerin-sportler-mannschaft-des-jahres-stadt-speyer/) | 2018-01-06 |                                                                                                                          | Der AV 03 Speyer hat... |
| Roding      | [Das Jahr 2017 in Zahlen](http://www.tb03-gewichtheben.de/2018/01/das-jahr-2017-in-zahlen/)                                                             | 2018-01-05 |                                                                                                                          | Im Jahr 2017 waren  ... |
| Mutterstadt | [Frohe Weihnachten](http://www.ac-mutterstadt.de/index.php?start=0&heading=49863411652d43e6d50849d6b604f71d1513983600.0)                                | 2017-12-23 |                                                                                                                          | Der AC 1892 Mutterst... |
| Schwedt     | [……………und wieder ist ein Jahr vorbei!!!](http://gewichtheben.blauweiss65-schwedt.de/?p=7676)                                                            | 2017-12-02 | <img src='http://gewichtheben.blauweiss65-schwedt.de/wp-content/uploads/2017/08/GW-Logo-neu-300x148.jpg' width='100px'/> | Auch dieses Jahr ist... |