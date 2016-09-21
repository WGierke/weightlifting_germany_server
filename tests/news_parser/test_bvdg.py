#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from blog_test_case import BlogTestCase
from parser.news_parser import NewsParser, BVDGParser
import time
import datetime
import urllib2


class TestBVDG(BlogTestCase):

    def test_article_urls_parsing(self):
        bvdg_parser = BVDGParser()
        page = urllib2.urlopen(BVDGParser.ARTICLES_URL + "1", timeout=NewsParser.TIMEOUT).read()
        self.assertEqual(len(bvdg_parser.parse_initial_articles(page)), 10)

    def test_url_parsing_with_picture(self):
        article = BVDGParser.parse_article_from_article_url("http://www.german-weightlifting.de/letzter-haertetest-countdown-fuer-unser-olympiateam/")
        self.assertEqual(article["url"], "http://www.german-weightlifting.de/letzter-haertetest-countdown-fuer-unser-olympiateam/")
        self.assertEqual(article["heading"].encode("utf-8"), "Letzter Härtetest – Countdown für unser Olympiateam")
        self.assertEqual(article["date"], str(time.mktime(datetime.date(2016, 8, 4).timetuple())))
        self.assertEqual(article["image"], "http://www.german-weightlifting.de/wp-content/uploads/2016/08/13898744_522939504563088_1035756263_o.jpg")
        self.assert_starts_with("Ein abschließendes Trainingslager absolvierte unser Olympiateam auf dem Feldberg", article["content"])
        self.assert_ends_with("Welche als Letzte den Flieger nach Brasilien besteigen werden.", article["content"])

    def test_url_parsing_with_picture2(self):
        article = BVDGParser.parse_article_from_article_url("http://www.german-weightlifting.de/erfolgreiches-trainingslager-in-kienbaum-dosb-verabschiedet-olympiakader-bei-sommerfest/")
        self.assertEqual(article["url"], "http://www.german-weightlifting.de/erfolgreiches-trainingslager-in-kienbaum-dosb-verabschiedet-olympiakader-bei-sommerfest/")
        self.assertEqual(article["heading"].encode("utf-8"), "Erfolgreiches Trainingslager in Kienbaum – DOSB verabschiedet Olympiakader bei Sommerfest")
        self.assertEqual(article["date"], str(time.mktime(datetime.date(2016, 7, 18).timetuple())))
        self.assertEqual(article["image"], "http://www.german-weightlifting.de/wp-content/uploads/2016/07/13632596_516930935163945_727382598_o.jpg")
        self.assert_starts_with("Vom 6.7. bis zum 16.7. , hieß es für unsere Nationalmannschaft erneut", article["content"])
        self.assert_ends_with("Bildern, einen kleinen Einblick bieten zu können.", article["content"])

    def test_url_parsing_without_picture(self):
        article = BVDGParser.parse_article_from_article_url("http://www.german-weightlifting.de/olympia-aus-fuer-russische-gewichtheber/")
        self.assertEqual(article["url"], "http://www.german-weightlifting.de/olympia-aus-fuer-russische-gewichtheber/")
        self.assertEqual(article["heading"].encode("utf-8"), "Olympia-Aus für Russische Gewichtheber")
        self.assertEqual(article["date"], str(time.mktime(datetime.date(2016, 7, 29).timetuple())))
        self.assertEqual(article["image"], "")
        self.assert_starts_with("Der russische Gewichtheberverband wurde heute von der Teilnahme an den Olympischen", article["content"])
        self.assert_text_in_content("Als Präsident des BVDG ist diese Entscheidung natürlich lange überfällig!", article["content"])
        self.assert_ends_with("bis zuletzt auf eine Olympianominierung hoffen durfte.", article["content"])

    def test_url_parsing_without_picture2(self):
        article = BVDGParser.parse_article_from_article_url("http://www.german-weightlifting.de/pokal-der-blauen-schwerter-feiert-auch-2016-eine-neuauflage/")
        self.assertEqual(article["url"], "http://www.german-weightlifting.de/pokal-der-blauen-schwerter-feiert-auch-2016-eine-neuauflage/")
        self.assertEqual(article["heading"].encode("utf-8"), "„Pokal der Blauen Schwerter“ feiert auch 2016 eine Neuauflage")
        self.assertEqual(article["date"], str(time.mktime(datetime.date(2016, 9, 20).timetuple())))
        self.assertEqual(article["image"], "")
        self.assert_starts_with("Die 2016er Neuauflage des Turniers um den „Pokal der Blauen Schwerter“", article["content"])
        self.assert_text_in_content("Großbritannien", article["content"])
        self.assert_ends_with("www.pokal-der-blauen-schwerter.de", article["content"])

if __name__ == '__main__':
    unittest.main()
