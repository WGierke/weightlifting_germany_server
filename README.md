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

| Blog Name   | Heading                                                                                                                                        | Date       | Image                                                                                                                            | Content                 |
|:------------|:-----------------------------------------------------------------------------------------------------------------------------------------------|:-----------|:---------------------------------------------------------------------------------------------------------------------------------|:------------------------|
| BVDG        | [Das Girls Camp 2016 steht vor der Tür!](http://www.german-weightlifting.de/das-girls-camp-2016-steht-vor-der-tuer/)                           | 2016-10-21 | <img src='http://www.german-weightlifting.de/wp-content/uploads/2016/10/Plakat-Girls-Camp-2016.png' width='100px'/>              | „Gewichtheben ist, g... |
| Mutterstadt | [Saisonauftakt Regionalliga gegen Altrip](http://www.ac-mutterstadt.de/index.php?start=0&heading=aa1d609d4bd86116380359b6b85e02e61476828000.0) | 2016-10-19 |                                                                                                                                  | Die Regionalligastaf... |
| Schwedt     | [Bundesliga AC Potsdam – OST Gewichtheben](http://gewichtheben.blauweiss65-schwedt.de/?p=7342)                                                 | 2016-10-16 | <img src='http://gewichtheben.blauweiss65-schwedt.de/wp-content/uploads/2009/02/Oder-Sund-Team-2013-300x169.jpg' width='100px'/> | Am Sonnabend traten ... |
| Speyer      | [Gewichtheben – Geburtstag an der Hantel](http://www.av03-speyer.de/2016/10/gewichtheben-geburtstag-an-der-hantel/)                            | 2016-10-11 |                                                                                                                                  | Speyer II 468,6:356,... |