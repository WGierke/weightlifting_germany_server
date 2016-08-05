#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

"""
This class dumps the articles of a specified blog in a JSON file.
"""
from datetime import datetime
from lxml import etree
from lxml.etree import tostring
import ConfigParser
import json
import locale
import re
import requests
import time
import traceback
import urllib2

config = ConfigParser.RawConfigParser(allow_no_value=True)
config.read('config.ini')
APPSPOT_KEY = config.get("appspot", "X-Secret-Key")
ENDPOINT = "http://localhost:8080"

class NewsParser:
    TIMEOUT = 15
    RE_HREF = re.compile(ur'(?<=href=")[^"]*(?=")')
    RE_IMG_TAG = re.compile(ur'(?<=<img)[^>]*')
    RE_IMG_SRC = re.compile(ur'(?<=src="http)[^"]*(?=")')
    RE_POST_ID = re.compile(ur'((?<=")post-\d+(?="))')

    def __init__(self, blog_name, blog_base_url, articles_url, articles_container_xpath):
        self.blog_name = blog_name
        self.blog_base_url = blog_base_url
        self.articles_url = self.blog_base_url + articles_url
        self.is_wordpress = self.is_wordpress()
        self.articles_container_xpath = articles_container_xpath
        self.newest_article = None

    def is_wordpress(self):
        try:
            page = urllib2.urlopen(self.blog_base_url + "wp-login.php", timeout=NewsParser.TIMEOUT).read()
            return "wordpress" in page
        except Exception, e:
            return False

    def parse_articles(self):
        articles = []
        n = 0
        while True:
            n += 1
            print n
            try:
                page = urllib2.urlopen(self.articles_url + str(n), timeout=NewsParser.TIMEOUT).read()
                if self.is_wordpress:
                    tree = etree.HTML(page)
                    articles_container = tree.xpath(self.articles_container_xpath)[0]
                    for article_container in articles_container:
                        if "id" in article_container.keys() and "post-" in article_container.attrib["id"]:
                            #post_id = article_container.attrib["id"]
                            article_url = re.findall(NewsParser.RE_HREF, tostring(article_container.getchildren()[0]))[0]
                            print article_url
                            payload = {"url": article_url}
                            article_exists_response = self.send_post(payload, "/article_exists")
                            if article_exists_response == "No":
                                print article_url + " does not exist yet"
                                new_article = self.parse_article_from_url(article_url)
                                payload = { "url": new_article["url"],
                                            "date": new_article["date"],
                                            "heading": new_article["heading"],
                                            "content": new_article["content"],
                                            "publisher": self.blog_name }
                                print payload
                                self.send_post(payload, "/add_article")
                            else:
                                print article_url + "already exists"
                                return

            except Exception, e:
                print 'Error while downloading news ', e
                return

    @classmethod
    def parse_article_from_url(self, article_url):
        try:
            article_page = urllib2.urlopen(article_url, timeout=NewsParser.TIMEOUT).read()
            article = self.parse_article_from_html(article_page)
            article["url"] = article_url
            return article
        except Exception, e:
            traceback.print_exc()
            return

    @classmethod
    def parse_article_from_html(self, html):
        raise NotImplementedError("Please Implement this method")

    def send_post(self, payload, path):
        headers = {"X-Secret-Key": APPSPOT_KEY, "Content-Type": "application/json"}
        r = requests.post(ENDPOINT + path, data=json.dumps(payload), headers=headers)
        return r.content


class SchwedtParser(NewsParser):
    @classmethod
    def parse_article_from_html(self, article_page):
        post_id = re.findall(NewsParser.RE_POST_ID, article_page)[0]
        article_tree = etree.HTML(article_page)
        german_date = article_tree.xpath("//*[@id=\"" + post_id + "\"]/div[1]/span")[0].text
        loc = locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
        date = datetime.strptime(german_date.encode('utf-8'), "%d. %B %Y")
        article = {"date": str(time.mktime(date.timetuple())),
                   "heading": article_tree.xpath("//*[@id=\"" + post_id + "\"]/h2")[0].text }
        text_container = article_tree.xpath("//*[@id=\"" + post_id + "\"]/div[2]")[0]
        text = []
        for child in text_container.getchildren():
            for text_child in child.itertext():
                text.append(text_child)
        article["content"] = ' '.join(text)

        image = ''
        for elem in text_container.iter():
            if elem.tag == 'img':
                image = elem.attrib['src']
                break
        article["image"] = image
        return article


class BVDGParser(NewsParser):
    @classmethod
    def parse_article_from_html(self, article_page):
        post_id = re.findall(NewsParser.RE_POST_ID, article_page)[0]
        article_tree = etree.HTML(article_page)
        loc = locale.setlocale(locale.LC_ALL, 'de_DE.utf8')

        post_content_holder = article_tree.xpath("//*[@id=\"" + post_id + "\"]/div[1]")[0]
        image = ''
        date = ''
        heading = ''
        text = []
        for elem in post_content_holder.iter():
            if elem.tag == 'img' and image == '':
                image = elem.attrib['src']
            if elem.tag == 'h2':
                headline_text_list = list(elem.itertext())
                date = headline_text_list[0] + " 2016"
                date = datetime.strptime(date.encode('utf-8'), "%d %b %Y")
                heading = headline_text_list[1].strip()
            if elem.tag == 'p':
                text.append(elem.text)

        article = {"date": str(time.mktime(date.timetuple())),
                   "heading": heading,
                   "image": image,
                   "content": ' '.join(text)}
        return article


if __name__ == '__main__':
    schwedtParser = SchwedtParser("Schwedt", "http://gewichtheben-schwedt.de/", "?page_id=6858&paged=", articles_container_xpath='//*[@id="main"]')
    #schwedtParser.parse_articles()

    bvdgParser = BVDGParser("BVDG", "http://www.german-weightlifting.de/", "category/leistungssport/page/", articles_container_xpath='/html/body/div[1]/div/div/div/div[2]/div/div')
    #bvdgParser.parse_articles()

