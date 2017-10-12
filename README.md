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

| Blog Name   | Heading                                                                                                                                                                              | Date       | Image                                                                                                                                        | Content                 |
|:------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------|:---------------------------------------------------------------------------------------------------------------------------------------------|:------------------------|
| Mutterstadt | [Bundesligaheimkampf gegen Heinsheim](http://www.ac-mutterstadt.de/index.php?start=0&heading=47bf14cf0278f98b41e127df1cc062b61507672800.0)                                           | 2017-10-11 |                                                                                                                                              | Am Samstag, dem 14.1... |
| BVDG        | [Erfolgreicher Türöffner-Tag beim Bundesverband Deutscher Gewichtheber](http://www.german-weightlifting.de/erfolgreicher-tueroeffner-tag-beim-bundesverband-deutscher-gewichtheber/) | 2017-10-04 | <img src='http://www.german-weightlifting.de/wp-content/uploads/2017/10/22219328_715266745330362_1511069781_o.jpg' width='100px'/>           | Auch 2017 hat das Te... |
| Speyer      | [Gewichtheben – Auch ohne fünf Spitzenleute](http://www.av03-speyer.de/2017/10/gewichtheben-auch-ohne-fuenf-spitzenleute/)                                                           | 2017-10-02 | <img src='http://www.av03-speyer.de/wp-content/uploads/2017/10/22104352_1434679669979174_2814484748638687242_o-1024x576.jpg' width='100px'/> | Auftakterfolg des Ti... |
| Roding      | [Spannender Bundesligaauftakt der Rodinger Heber](http://www.tb03-gewichtheben.de/2017/10/spannender-bundesligaauftakt-der-rodinger-heber/)                                          | 2017-10-02 |                                                                                                                                              | Drei Punkte aus Suhl... |
| Schwedt     | [Bundesliga 2017/18](http://gewichtheben.blauweiss65-schwedt.de/?p=7639)                                                                                                             | 2017-08-05 | <img src='http://gewichtheben.blauweiss65-schwedt.de/wp-content/uploads/2017/08/GW-Logo-neu-300x148.jpg' width='100px'/>                     | Zurück zum TSV Blau ... |