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

| Blog Name   | Heading                                                                                                                                           | Date       | Image                                                                                                                            | Content                 |
|:------------|:--------------------------------------------------------------------------------------------------------------------------------------------------|:-----------|:---------------------------------------------------------------------------------------------------------------------------------|:------------------------|
| Mutterstadt | [Toller Saisonausklang](http://www.ac-mutterstadt.de/index.php?start=0&heading=cb892d33e9cb915ab2e3acc65c97ff351523138400.0)                      | 2018-04-08 | <img src='http://www.ac-mutterstadt.de//images/Prot-schiff.png' width='100px'/>                                                  | Mit einem souveränen... |
| Roding      | [Wie ein Uhrwerk exakt auf 500 Punkte zu gesteuert](http://www.tb03-gewichtheben.de/2018/04/wie-ein-uhrwerk-exakt-auf-500-punkte-zu-gesteuert/)   | 2018-04-08 | <img src='http://www.tb03-gewichtheben.de/wp-content/gallery/tb-03-roding-ii-sv-empor-berlin/K1600_P1080084.JPG' width='100px'/> | Roding II besiegt be... |
| Speyer      | [Gewichtheben – Europameisterschaft:  Vier Goldmedaillen](http://www.av03-speyer.de/2018/04/gewichtheben-europameisterschaft-vier-goldmedaillen/) | 2018-04-03 |                                                                                                                                  | SPEYER. Sieben für d... |
| Schwedt     | [22. Lothar-Treder-Gedenkturnier](http://gewichtheben.blauweiss65-schwedt.de/?p=7679)                                                             | 2018-02-15 |                                                                                                                                  | Das traditionelle Tu... |