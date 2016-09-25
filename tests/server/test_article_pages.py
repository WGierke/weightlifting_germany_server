#!/usr/bin/python
# -*- coding: utf-8 -*-

from test_main_server import ServerTestCase
import json
import time
import datetime


class ArticleTestCase(ServerTestCase):
    def test_adding_articles(self):
        url = "http://gewichtheben.blauweiss65-schwedt.de/?page_id=6858&paged=1"
        date = "1456182000"
        heading = "My Article Ä"
        content = "My Content Ä"
        publisher = "My Publisher"

        response = self.get_authenticated("/get_articles?publisher=" + publisher)
        self.assertEqual(response.normal_body, '{"result": []}')

        params = {"url": url, "date": date, "heading": heading, "content": content, "publisher": publisher}
        response = self.post_authenticated("/add_article", params=params)
        self.assertEqual(response.normal_body, 'Added article successfully')
        response = self.get_authenticated("/get_articles?publisher=" + publisher)
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["url"], url)

        response = self.post_authenticated("/add_article", params=params)
        self.assertEqual(response.normal_body, 'This article is already saved')
        response = self.get_authenticated("/get_articles?publisher=" + publisher)
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["url"], url)

        params = {"url": url + "_2", "date": date, "heading": heading, "content": content, "publisher": publisher}
        response = self.post_authenticated("/add_article", params=params)
        self.assertEqual(response.normal_body, 'Added article successfully')
        response = self.get_authenticated("/get_articles?publisher=" + publisher)
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["url"], url)
        self.assertEqual(result[1]["url"], url + "_2")

    def test_deleting_articles(self):
        url = "http://gewichtheben.blauweiss65-schwedt.de/?page_id=6858&paged=1"
        date = "1456182000"
        heading = "My Article Ä"
        content = "My Content Ä"
        publisher = "My Publisher"

        response = self.get_authenticated("/get_articles?publisher=" + publisher)
        self.assertEqual(response.normal_body, '{"result": []}')
        params = {"url": url, "date": date, "heading": heading, "content": content, "publisher": publisher}
        response = self.post_authenticated("/add_article", params=params)
        params["url"] = url + "_2"
        response = self.post_authenticated("/add_article", params=params)
        response = self.get_authenticated("/get_articles?publisher=" + publisher)
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["url"], url)
        self.assertEqual(result[1]["url"], url + "_2")

        response = self.post_authenticated("/delete_article", params={"url": url})
        self.assertEqual(response.normal_body, 'Deleted article successfully')
        response = self.get_authenticated("/get_articles?publisher=" + publisher)
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["url"], url + "_2")

        response = self.post_authenticated("/delete_article", params={"url": url})
        self.assertEqual(response.normal_body, 'No article found')
        response = self.get_authenticated("/get_articles?publisher=" + publisher)
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["url"], url + "_2")

        response = self.post_authenticated("/delete_article", params={"url": url + "_2"})
        self.assertEqual(response.normal_body, 'Deleted article successfully')
        response = self.get_authenticated("/get_articles?publisher=" + publisher)
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 0)

    def test_article_exists(self):
        response = self.get_authenticated("/get_articles")
        self.assertEqual(response.normal_body, '{"result": []}')

        url = "http://gewichtheben.blauweiss65-schwedt.de/?page_id=6858&paged=1"
        date = "1456182000"
        heading = "My Article Ä"
        content = "My Content Ä"
        publisher = "My Publisher"
        image = "My Image"
        params = {"url": url, "date": date, "heading": heading, "content": content, "publisher": publisher, "image": image}

        response = self.post_authenticated("/article_exists", params=params)
        self.assertEqual(response.normal_body, "No")

        response = self.post_authenticated("/add_article", params=params)
        response = self.post_authenticated("/article_exists", params=params)
        self.assertEqual(response.normal_body, "Yes")

        response = self.post_authenticated("/delete_article", params=params)
        response = self.post_authenticated("/article_exists", params=params)
        self.assertEqual(response.normal_body, "No")

    def test_article_getting(self):
        response = self.get_authenticated("/get_articles")
        self.assertEqual(response.normal_body, '{"result": []}')

        url = "http://gewichtheben.blauweiss65-schwedt.de/?page_id=6858&paged=1"
        date = str(time.mktime(datetime.date(2016, 6, 24).timetuple()))
        heading = "My Article Ä"
        content = "My Content Ä"
        publisher = "My Publisher"
        image = "My image"
        params = {"url": url, "date": date, "heading": heading, "content": content, "publisher": publisher, "image": image}

        response = self.post_authenticated("/add_article", params=params)
        response = self.get_authenticated("/get_article", params={"url": url})
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(result["url"], url)
        self.assertEqual(result["date"], date)
        self.assertEqual(result["heading"], heading.decode("utf-8"))
        self.assertEqual(result["content"], content.decode("utf-8"))
        self.assertEqual(result["publisher"], publisher.decode("utf-8"))
        self.assertEqual(result["image"], image.decode("utf-8"))
