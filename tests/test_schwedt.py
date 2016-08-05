#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from blog_test_case import BlogTestCase
from news_parser import NewsParser, SchwedtParser
import time
import datetime
import urllib2


class TestSchwedt(BlogTestCase):

    def test_article_urls_parsing(self):
        schwedt_parser = SchwedtParser("Schwedt", "http://gewichtheben-schwedt.de/", "?page_id=6858&paged=", articles_container_xpath='//*[@id="main"]')
        page = urllib2.urlopen(schwedt_parser.articles_url + "1", timeout=NewsParser.TIMEOUT).read()
        self.assertEqual(len(schwedt_parser.parse_article_urls(page)), 4)

    def test_url_parsing_with_text(self):
        article = SchwedtParser.parse_article_from_url("http://gewichtheben.blauweiss65-schwedt.de/?p=7312")
        self.assertEqual(article["url"], "http://gewichtheben.blauweiss65-schwedt.de/?p=7312")
        self.assertEqual(article["heading"], "39. Treffen zwischen den Jugendauswahlmannschaften der Region Csongrad (Ungarn) und des Landes Brandenburg")
        self.assertEqual(article["date"], str(time.mktime(datetime.date(2016, 6, 24).timetuple())))
        self.assertEqual(article["image"], "http://gewichtheben.blauweiss65-schwedt.de/wp-content/uploads/2016/06/Mannschaft-des-BGFV-300x225.jpg")
        self.assert_text_in_content("Die Abteilung Gewichtheben des TSV Blau-Weiß 65 Schwedt bildete bei der 39. Auflage dieses Vergleiches mit", article["content"])
        self.assert_text_in_content("haben, gemeinsam mit dem 50jährigen Jubiläum der Gewichtheber des TSV Blau-Weiß 65 Schwedt.", article["content"])

    def test_url_parsing_without_text(self):
        article = SchwedtParser.parse_article_from_url("http://gewichtheben.blauweiss65-schwedt.de/?p=7195")
        self.assertEqual(article["url"], "http://gewichtheben.blauweiss65-schwedt.de/?p=7195")
        self.assertEqual(article["heading"], "Bundesliga OST Gewichtheber vs. TSC Berlin")
        self.assertEqual(article["date"], str(time.mktime(datetime.date(2016, 2, 23).timetuple())))
        self.assertEqual(article["image"], "http://gewichtheben.blauweiss65-schwedt.de/wp-content/uploads/2016/02/Plakat-05_03_2016-212x300.jpg")
        self.assertEqual(article["content"], "")

if __name__ == '__main__':
    unittest.main()
