#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from blog_test_case import BlogTestCase
from parser.news_parser import NewsParser, SpeyerParser
import time
import datetime
import urllib2


class TestSpeyer(BlogTestCase):

    def test_article_urls_parsing(self):
        speyer_parser = SpeyerParser()
        page = urllib2.urlopen(SpeyerParser.ARTICLES_URL + "1", timeout=NewsParser.TIMEOUT).read()
        self.assertEqual(len(speyer_parser.parse_article_urls(page)), 10)

    def test_url_parsing_with_picture(self):
        article = SpeyerParser.parse_article_from_url("http://www.av03-speyer.de/2016/03/gewichtheben-bvdg-auszeichnung-gewichtheberin-des-jahres-2015/")
        self.assertEqual(article["url"], "http://www.av03-speyer.de/2016/03/gewichtheben-bvdg-auszeichnung-gewichtheberin-des-jahres-2015/")
        self.assertEqual(article["heading"].encode("utf-8"), "Gewichtheben – BVDG-Auszeichnung „Gewichtheber/in des Jahres 2015“")
        self.assertEqual(article["date"], str(time.mktime(datetime.date(2016, 3, 17).timetuple())))
        self.assertEqual(article["image"], "http://www.av03-speyer.de/wp-content/uploads/2015/11/Schwarzbach-Julia-200x300.jpg")
        self.assert_text_in_content("Der BVDG zeichnet die „Speyerer“ Julia Schwarzbach und Almir Velagic", article["content"])
        self.assert_text_in_content("Shop: www.bvdg-shop.de", article["content"])

    def test_url_parsing_without_picture(self):
        article = SpeyerParser.parse_article_from_url("http://www.av03-speyer.de/2016/02/gewichtheben-gut-geruestet-fuers-finale/")
        self.assertEqual(article["url"], "http://www.av03-speyer.de/2016/02/gewichtheben-gut-geruestet-fuers-finale/")
        self.assertEqual(article["heading"].encode("utf-8"), "Gewichtheben – „Gut gerüstet fürs Finale“")
        self.assertEqual(article["date"], str(time.mktime(datetime.date(2016, 2, 15).timetuple())))
        self.assertEqual(article["image"], "")
        self.assert_text_in_content("Deutlicher Sieg über Heinsheim – Wesentlich mehr als Chemnitz", article["content"])
        self.assert_text_in_content("210 = 390 = 148,0 (3.). (wk)", article["content"])

if __name__ == '__main__':
    unittest.main()
