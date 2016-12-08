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
    - [ ] [TB 03 Roding](http://www.tb03-gewichtheben.de/page/1/)
    - [ ] [TSV Heinsheim](http://gewichtheben.tsv-heinsheim.de/index.php?start=1)


## Current News

| Blog Name   | Heading                                                                                                                           | Date       | Image                                                                                                                            | Content                 |
|:------------|:----------------------------------------------------------------------------------------------------------------------------------|:-----------|:---------------------------------------------------------------------------------------------------------------------------------|:------------------------|
| BVDG        | [Verleihung der Nachwuchstrainer-Awards](http://www.german-weightlifting.de/verleihung-der-bvdg-nachwuchstrainer-awards/)         | 2016-12-08 | <img src='http://www.german-weightlifting.de/wp-content/uploads/2016/12/2-Nagold-Weinheim.jpg' width='100px'/>                   | Anlässlich des Zweib... |
| Speyer      | [Gewichtheben – David SANCHEZ Europameister U23](http://www.av03-speyer.de/2016/12/gewichtheben-david-sanchez-europameister-u23/) | 2016-12-06 | <img src='http://www.av03-speyer.de/wp-content/uploads/2015/06/David-SANCHEZ-LOPEZ.jpg' width='100px'/>                          | Der AV 03 Speyer gra... |
| Mutterstadt | [Louis Dancz Jahresbester](http://www.ac-mutterstadt.de/index.php?start=0&heading=24e881a28feb7c00f0656cf3e277dcd11480892400.0)   | 2016-12-05 | <img src='http://www.ac-mutterstadt.de//images/Louis_1.jpg' width='100px'/>                                                      | Mit neuen Bestleistu... |
| Schwedt     | [1. Bundesliga 3. Wettkampftag TSC Berlin – OST Gewichtheben](http://gewichtheben.blauweiss65-schwedt.de/?p=7348)                 | 2016-11-15 | <img src='http://gewichtheben.blauweiss65-schwedt.de/wp-content/uploads/2009/02/Oder-Sund-Team-2013-300x169.jpg' width='100px'/> | Am 3. Wettkampftag d... |