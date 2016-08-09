#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

"""
This class dumps the articles of a specified blog in a JSON file.
"""
from datetime import datetime
from lxml import etree
from lxml.etree import tostring
from tabulate import tabulate
import codecs
import ConfigParser
import json
import locale
import re
import requests
import time
import traceback
import urllib2
import os.path
from bs4 import BeautifulSoup

ENDPOINT = "http://localhost:8080"

if os.path.isfile("config.ini"):
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.read('config.ini')
    APPSPOT_KEY = config.get("appspot", "X-Secret-Key")

class NewsParser:
    TIMEOUT = 15
    RE_HREF = re.compile(ur'(?<=href=")[^"]*(?=")')
    RE_IMG_TAG = re.compile(ur'(?<=<img)[^>]*')
    RE_IMG_SRC = re.compile(ur'(?<=src="http)[^"]*(?=")')
    RE_POST_ID = re.compile(ur'((?<=")post-\d+(?="))')

    BLOG_NAME = "BLOG_NAME"
    BLOG_BASE_URL = "BLOG_BASE_URL"
    ARTICLES_URL = "ARTICLES_URL"
    ARTICLES_CONTAINER_XPATH = "ARTICLES_CONTAINER_XPATH"
    ARTICLES_POST_CLASS = "ARTICLES_POST_CLASS"

    def __init__(self):
        self.newest_article = None

    def is_wordpress(self):
        try:
            page = urllib2.urlopen(self.blog_base_url + "wp-login.php", timeout=NewsParser.TIMEOUT).read()
            return "wordpress" in page
        except Exception, e:
            return False

    def parse_articles(self):
        n = 0
        while True:
            n += 1
            print n
            try:
                page = urllib2.urlopen(self.ARTICLES_URL + str(n), timeout=NewsParser.TIMEOUT).read()
                article_urls = self.parse_article_urls(page)
                for article_url in article_urls:
                    payload = {"url": article_url}
                    article_exists_response = self.send_post(payload, "/article_exists")
                    if article_exists_response == "No":
                        print article_url + " does not exist yet"
                        new_article = self.parse_article_from_url(article_url)
                        payload = {"url": new_article["url"],
                                   "date": new_article["date"],
                                   "heading": new_article["heading"],
                                   "content": new_article["content"],
                                   "publisher": self.BLOG_NAME}
                        print payload
                        self.send_post(payload, "/add_article")
                    else:
                        print article_url + "already exists"
                        return

            except Exception, e:
                print 'Error while downloading news ', e
                return

    def parse_article_urls(self, page):
        article_urls = []
        tree = etree.HTML(page)
        articles_container = tree.xpath(self.ARTICLES_CONTAINER_XPATH)[0]
        for article_container in articles_container:
            if "class" in article_container.keys() and self.ARTICLES_POST_CLASS in article_container.attrib["class"]:
                for elem in article_container.iter():
                    if elem.tag == 'a':
                        article_urls.append(elem.attrib["href"])
                        break
        return article_urls

    @classmethod
    def parse_article_from_url(self, article_url):
        try:
            article_page = urllib2.urlopen(article_url, timeout=NewsParser.TIMEOUT).read().decode("utf-8")
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
    BLOG_NAME = "Schwedt"
    BLOG_BASE_URL = "http://gewichtheben-schwedt.de/"
    ARTICLES_URL = BLOG_BASE_URL + "?page_id=6858&paged="
    ARTICLES_CONTAINER_XPATH = '//*[@id="main"]'
    ARTICLES_POST_CLASS = "post"

    @classmethod
    def parse_article_from_html(self, article_page):
        post_id = re.findall(NewsParser.RE_POST_ID, article_page)[0]
        article_tree = etree.HTML(article_page)
        german_date = article_tree.xpath("//*[@id=\"" + post_id + "\"]/div[1]/span")[0].text
        loc = locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
        date = datetime.strptime(german_date.encode('utf-8'), "%d. %B %Y")
        article = {"date": str(time.mktime(date.timetuple())),
                   "heading": article_tree.xpath("//*[@id=\"" + post_id + "\"]/h2")[0].text }

        post_content_holder = article_tree.xpath("//*[@id=\"" + post_id + "\"]/div[2]")[0]
        soup = BeautifulSoup(tostring(post_content_holder), "lxml")
        article["content"] = ''.join(soup.findAll(text=True)).strip()

        image = ''
        for elem in post_content_holder.iter():
            if elem.tag == 'img':
                image = elem.attrib['src']
                break
        article["image"] = image
        return article


class BVDGParser(NewsParser):
    BLOG_NAME = "BVDG"
    BLOG_BASE_URL = "http://www.german-weightlifting.de/"
    ARTICLES_URL = BLOG_BASE_URL + "category/leistungssport/page/"
    ARTICLES_CONTAINER_XPATH = '/html/body/div[1]/div/div/div/div[2]/div/div'
    ARTICLES_POST_CLASS = "post"

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
                text.append(elem.text + "\n")

        soup = BeautifulSoup(tostring(post_content_holder), "lxml")
        content = ''.join(soup.findAll(text=True)).strip()
        content = '\n'.join(content.split(u"\n\n\n\xa0\n")[1:]) # Remove category and author

        article = {"date": str(time.mktime(date.timetuple())),
                   "heading": heading,
                   "image": image,
                   "content": content}
        return article

class SpeyerParser(NewsParser):
    BLOG_NAME = "Speyer"
    BLOG_BASE_URL = "http://www.av03-speyer.de/"
    ARTICLES_URL = BLOG_BASE_URL + "category/gewichtheben/page/"
    ARTICLES_CONTAINER_XPATH = '/html/body/div[1]/div/div/div/div[1]/section'
    ARTICLES_POST_CLASS = "entry-box text-left"

    @classmethod
    def parse_article_from_html(self, article_page):
        post_id = re.findall(NewsParser.RE_POST_ID, article_page)[0]
        article_tree = etree.HTML(article_page)
        loc = locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
        post_content_holder = article_tree.xpath("//*[@id=\"" + post_id + "\"]/div[2]/div/div/div[1]")[0]

        year_month = article_tree.xpath("/html/head/link[1]")[0].attrib["href"].split("/")[3:5]
        day = post_content_holder.xpath("section/article/div/div[1]/div/span[1]/a/text()")[0].split(" ")[1][0:-1]
        date = " ".join(year_month) + " " + day
        date = datetime.strptime(date.encode('utf-8'), "%Y %m %d")

        image = ''
        heading = ''
        for elem in post_content_holder.iter():
            if elem.tag == 'img' and image == '':
                image = elem.attrib['src']
            if elem.tag == 'h1' and "class" in elem.attrib and elem.attrib["class"] == "entry-title":
                heading = elem.text

        soup = BeautifulSoup(tostring(post_content_holder), "lxml")
        content = ''.join(soup.findAll(text=True)).strip()
        content = '\n'.join(content.split("\n\n\n\n")[1:])

        article = {"date": str(time.mktime(date.timetuple())),
                   "heading": heading,
                   "image": image,
                   "content": content}

        return article


if __name__ == '__main__':
    blog_parsers_classes = [BVDGParser, SpeyerParser, SchwedtParser]

    headers = ["Blog Name", "Heading", "Date", "Image", "Content"]
    table = list()
    for blog_parser_class in blog_parsers_classes:
        blog_parser_instance = blog_parser_class()
        page = urllib2.urlopen(blog_parser_class.ARTICLES_URL + "1").read()
        first_article_url = blog_parser_instance.parse_article_urls(page)[0]
        article = blog_parser_class.parse_article_from_url(first_article_url)
        row = [blog_parser_instance.BLOG_NAME,
               "[{}]({})".format(article["heading"], article["url"]),
               datetime.fromtimestamp(float(article["date"])).strftime("%Y-%m-%d"),
               "<img src='{}' width='100px'/>".format(article["image"]) if article["image"] else "",
               article["content"][:20] + "..."
               ]
        table.append(row)
    table = sorted(table, key=lambda k: datetime.strptime(k[2], "%Y-%m-%d"), reverse=True)

    with codecs.open("README.md", 'r', encoding='utf8') as f:
        readme = f.read()
    before_news = readme.split("## Current News")[0]
    new_readme = before_news + "\n## Current News\n\n" + tabulate(table, headers, tablefmt="pipe")
    with codecs.open("README.md", 'w', encoding='utf8') as f:
        f.write(new_readme)
