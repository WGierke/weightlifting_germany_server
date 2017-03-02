#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

"""
This class crawls the articles of a specified blog and uploads them as JSON files
"""
import ConfigParser
import locale
import md5
import re
import requests
import time
import traceback
import urllib2
import os.path
import logging
import sys
from bs4 import BeautifulSoup
from datetime import datetime
from lxml import etree
from lxml.etree import tostring
from utils import send_to_slack, notify_users_about_article, get_endpoint, is_production, write_news

ENDPOINT = get_endpoint()
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger("requests").setLevel(logging.WARNING)

if os.path.isfile("config.ini"):
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.read('config.ini')
    APPSPOT_KEY = config.get("appspot", "X-Secret-Key")

class NewsParser:
    TIMEOUT = 15
    RE_POST_ID = re.compile(ur'((?<=")post-\d+(?="))')

    BLOG_NAME = "BLOG_NAME"
    BLOG_BASE_URL = "BLOG_BASE_URL"
    ARTICLES_URL = "ARTICLES_URL"
    ARTICLES_CONTAINER_XPATH = "ARTICLES_CONTAINER_XPATH"
    ARTICLES_POST_CLASS = "ARTICLES_POST_CLASS"

    def __init__(self):
        self.newest_article_url = None

    def get_newest_article_url(self):
        return self.newest_article_url

    def is_wordpress(self):
        try:
            page = urllib2.urlopen(self.blog_base_url + "wp-login.php", timeout=NewsParser.TIMEOUT).read()
            return "wordpress" in page
        except Exception, e:
            return False

    def parse_articles(self):
        page_index = 0
        logging.info("Parsing Blog " + self.BLOG_NAME)
        while True:
            page_index += 1
            logging.info("Page " + str(page_index))
            try:
                try:
                    page = urllib2.urlopen(self.ARTICLES_URL + str(page_index), timeout=NewsParser.TIMEOUT).read()
                except urllib2.HTTPError, e:
                    if e.code == 404:
                        logging.info("Finished parsing blog")
                        return
                    else:
                        raise Exception(e)

                articles = self.parse_initial_articles(page)
                for article_index in range(len(articles)):
                    article_url = articles[article_index]["url"]
                    if page_index == 1 and article_index == 0:
                        if self.newest_article_url == article_url:
                            logging.info("Local check: " + article_url + " already exists")
                            logging.info("Finished parsing blog")
                            return
                        else:
                            self.newest_article_url = article_url

                    payload = {"url": article_url}
                    article_exists_response = self.send_post(payload, "/article_exists")
                    if article_exists_response == "No":
                        logging.info(article_url + " does not exist yet")
                        new_article = self.parse_article_from_article_url(articles[article_index])
                        payload = {"url": new_article["url"],
                                   "date": new_article["date"],
                                   "heading": new_article["heading"],
                                   "content": new_article["content"],
                                   "image": new_article["image"],
                                   "publisher": self.BLOG_NAME}
                        self.send_post(payload, "/add_article")
                        if is_production():
                            notify_users_about_article(payload)
                            write_news(self.BLOG_NAME + ": " + new_article["heading"] + "\n")
                    elif article_exists_response == "Yes":
                        logging.info(article_url + " already exists")
                        logging.info("Finished parsing blog")
                        return
                    else:
                        logging.info("/article_exists sent unexpected answer: " + article_exists_response)
                        return

            except Exception, e:
                text = "Error while parsing news for " + self.BLOG_NAME + " on page " + str(page_index) + ": "
                text += traceback.format_exc()
                logging.info(text)
                send_to_slack(text)
                return


    def parse_initial_articles(self, page):
        articles = []
        tree = etree.HTML(page)
        articles_container = tree.xpath(self.ARTICLES_CONTAINER_XPATH)[0]
        for article_container in articles_container:
            if "class" in article_container.keys() and self.ARTICLES_POST_CLASS in article_container.attrib["class"]:
                article = NewsParser.get_initial_article_dict()
                for elem in article_container.iter():
                    if elem.tag == 'a' and not article["url"]:
                        article["url"] = elem.attrib["href"]
                    if elem.tag == 'img' and not article["image"]:
                        article["image"] = elem.attrib["src"]
                articles.append(article)
        return articles

    @classmethod
    def parse_article_from_article_url(cls, initial_article):
        if isinstance(initial_article, basestring):
            initial_article = NewsParser.get_initial_article_dict(url=initial_article)
        article_page = urllib2.urlopen(initial_article["url"], timeout=NewsParser.TIMEOUT).read().decode("utf-8")
        article = cls.parse_article_from_html(article_page, initial_article)
        return article

    @classmethod
    def parse_article_from_html(cls, html, initial_article):
        raise NotImplementedError("Please Implement this method")

    def send_post(self, payload, path, endpoint=ENDPOINT):
        r = requests.post(endpoint + path, data=payload, headers={"X-Secret-Key": APPSPOT_KEY})
        return r.content

    @classmethod
    def get_initial_article_dict(cls, url="", image=""):
        return {"url": url, "image": image}


class SchwedtParser(NewsParser):
    BLOG_NAME = "Schwedt"
    BLOG_BASE_URL = "http://gewichtheben-schwedt.de/"
    ARTICLES_URL = BLOG_BASE_URL + "?page_id=6858&paged="
    ARTICLES_CONTAINER_XPATH = '//*[@id="main"]'
    ARTICLES_POST_CLASS = "post"

    @classmethod
    def parse_article_from_html(self, article_page, article):
        post_id = re.findall(NewsParser.RE_POST_ID, article_page)[0]
        article_tree = etree.HTML(article_page)
        german_date = article_tree.xpath("//*[@id=\"" + post_id + "\"]/div[1]/span")[0].text
        loc = locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
        date = datetime.strptime(german_date.encode('utf-8'), "%d. %B %Y")
        article["date"] = str(time.mktime(date.timetuple()))
        article["heading"] = article_tree.xpath("//*[@id=\"" + post_id + "\"]/h2")[0].text

        post_content_holder = article_tree.xpath("//*[@id=\"" + post_id + "\"]/div[2]")[0]
        soup = BeautifulSoup(tostring(post_content_holder), "lxml")
        article["content"] = ''.join(soup.findAll(text=True)).strip()

        if not article["image"]:
            for elem in post_content_holder.iter():
                if elem.tag == 'img':
                    article["image"] = elem.attrib['src']
                    break
        return article


class BVDGParser(NewsParser):
    BLOG_NAME = "BVDG"
    BLOG_BASE_URL = "http://www.german-weightlifting.de/"
    ARTICLES_URL = BLOG_BASE_URL + "category/topnews/page/"
    ARTICLES_CONTAINER_XPATH = '/html/body/div[1]/div/div/div/div[2]/div/div'
    ARTICLES_POST_CLASS = "post"

    @classmethod
    def parse_article_from_html(self, article_page, article):
        post_id = re.findall(NewsParser.RE_POST_ID, article_page)[0]
        article_tree = etree.HTML(article_page)
        loc = locale.setlocale(locale.LC_ALL, 'de_DE.utf8')

        post_content_holder = article_tree.xpath("//*[@id=\"" + post_id + "\"]/div[1]")[0]
        image = article["image"]
        date = ''
        heading = ''

        for elem in post_content_holder.iter():
            if elem.tag == 'img' and not image:
                image = elem.attrib['src']
            if elem.tag == 'h2':
                headline_text_list = list(elem.itertext())
                date = headline_text_list[0] + " " + str(datetime.now().year)
                date = date.replace("Mrz", "März")
                date = datetime.strptime(date.encode('utf-8'), "%d %b %Y")
                heading = headline_text_list[1].strip()

        soup = BeautifulSoup(tostring(post_content_holder), "lxml")
        content = ''.join(soup.findAll(text=True)).strip()
        #Remove time, category and comments
        comment_content_delimiters = [u"\n\n\n", u"\n\n\xa0\n"]
        for comment_content_delimiter in comment_content_delimiters:
            if comment_content_delimiter in content:
                content = '\n'.join(content.split(comment_content_delimiter)[1:]).strip()
                break

        article["date"] = str(time.mktime(date.timetuple()))
        article["heading"] = heading
        article["image"] = image
        article["content"] = content
        return article

class SpeyerParser(NewsParser):
    BLOG_NAME = "Speyer"
    BLOG_BASE_URL = "http://www.av03-speyer.de/"
    ARTICLES_URL = BLOG_BASE_URL + "category/gewichtheben/page/"
    ARTICLES_CONTAINER_XPATH = '/html/body/div[1]/div/div/div/div[1]/section'
    ARTICLES_POST_CLASS = "entry-box text-left"

    @classmethod
    def parse_article_from_html(self, article_page, article):
        post_id = re.findall(NewsParser.RE_POST_ID, article_page)[0]
        article_tree = etree.HTML(article_page)
        loc = locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
        post_content_holder = article_tree.xpath("//*[@id=\"" + post_id + "\"]/div[2]/div/div/div[1]")[0]

        year_month = article_tree.xpath("/html/head/link[1]")[0].attrib["href"].split("/")[3:5]
        day = post_content_holder.xpath("section/article/div/div[1]/div/span[1]/a/text()")[0].split(" ")[1][0:-1]
        date = " ".join(year_month) + " " + day
        date = datetime.strptime(date.encode('utf-8'), "%Y %m %d")

        image = article["image"]
        heading = ''
        for elem in post_content_holder.iter():
            if elem.tag == 'img' and image == '':
                image = elem.attrib['src']
            if elem.tag == 'h1' and "class" in elem.attrib and elem.attrib["class"] == "entry-title":
                heading = elem.text

        soup = BeautifulSoup(tostring(post_content_holder), "lxml")
        content = ''.join(soup.findAll(text=True)).strip()
        content = '\n'.join(content.split("\n\n\n\n")[1:])

        article["date"] = str(time.mktime(date.timetuple()))
        article["heading"] = heading
        article["image"] = image
        article["content"] = content

        return article

class MutterstadtParser(NewsParser):
    BLOG_NAME = "Mutterstadt"
    BLOG_BASE_URL = "http://www.ac-mutterstadt.de/"
    ARTICLES_URL = BLOG_BASE_URL + "index.php?start="
    ARTICLES_CONTAINER_XPATH = '//*[@id="art-main"]/div/div/div/div/div[1]/div'
    ARTICLES_POST_CLASS = "items-row cols-1 row-"

    def parse_articles(self):
        page_index = -5
        logging.info("Parsing Blog " + self.BLOG_NAME)
        while True:
            page_index += 5
            logging.info("Page " + str(page_index))
            try:
                try:
                    page = urllib2.urlopen(self.ARTICLES_URL + str(page_index), timeout=NewsParser.TIMEOUT).read()
                except urllib2.HTTPError, e:
                    if e.code == 404:
                        logging.info("Finished parsing blog")
                        return
                    else:
                        raise Exception(e)

                tree = etree.HTML(page)
                articles_container = tree.xpath(MutterstadtParser.ARTICLES_CONTAINER_XPATH)[0]
                articles = []
                for article in articles_container:
                    if "class" in articles_container.keys() and "items-row cols-1 row-" in article.attrib["class"]:
                        articles.append(article)

                if len(articles) == 0:
                    return

                for article_index in range(len(articles)):
                    article = articles[article_index]
                    texts = list(article.itertext())

                    heading = texts[2]
                    content = texts[11:]
                    content = [text_part.strip() for text_part in content]
                    content = [text_part for text_part in content if text_part != '']
                    content = '\n'.join(content)
                    loc = locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
                    date = ' '.join(texts[3].split(' ')[2:5])
                    date = datetime.strptime(date.encode('utf-8'), "%d. %B %Y")
                    date = str(time.mktime(date.timetuple()))
                    url = self.ARTICLES_URL + str(0) + "&heading=" + md5.new(heading.encode("utf-8")).hexdigest() + date
                    image = ''
                    for elem in list(article.getiterator()):
                        if elem.tag == 'img':
                            image = self.BLOG_BASE_URL + elem.attrib["src"]
                            break

                    if self.newest_article_url == url:
                        logging.info("Local check: " + heading + " already exists")
                        logging.info("Finished parsing blog")
                        return
                    else:
                        self.newest_article_url = url

                    payload = {"url": url}
                    article_exists_response = self.send_post(payload, "/article_exists")
                    if article_exists_response == "No":
                        logging.info(heading + " does not exist yet")
                        payload = {"url": url,
                                   "date": date,
                                   "heading": heading,
                                   "content": content,
                                   "image": image,
                                   "publisher": self.BLOG_NAME}
                        self.send_post(payload, "/add_article")
                        if is_production():
                            notify_users_about_article(payload)
                            write_news(self.BLOG_NAME + ": " + heading + "\n")
                    elif article_exists_response == "Yes":
                        logging.info(url + " already exists")
                        logging.info("Finished parsing blog")
                        return
                    else:
                        logging.info("/article_exists sent unexpected answer: " + article_exists_response)
                        return

            except Exception, e:
                text = "Error while parsing news for " + self.BLOG_NAME + " on page " + str(page_index) + ": "
                text += traceback.format_exc()
                logging.info(text)
                send_to_slack(text)
                return
