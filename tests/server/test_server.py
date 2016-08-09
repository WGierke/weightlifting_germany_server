#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import json
import os
import time
import unittest
import webtest
import yaml

from google.appengine.ext import testbed
from germany_app_engine.germany_app_engine import GermanyServer


class ServerTestCase(unittest.TestCase):
    SECRET_KEY = ''

    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which will allow you to use service stubs.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

        app = GermanyServer().start()
        self.testapp = webtest.TestApp(app)

        # Load Secret Key
        if os.environ.get("SECRET_KEY"):
            self.SECRET_KEY = os.environ.get("SECRET_KEY")
        else:
            with open('germany_app_engine/app.yaml') as f: 
                self.SECRET_KEY = yaml.load(f)["env_variables"]["SECRET_KEY"]

    def tearDown(self):
        # Don't forget to deactivate the testbed after the tests are
        # completed. If the testbed is not deactivated, the original
        # stubs will not be restored.
        self.testbed.deactivate()

    def get_authenticated(self, route, params=None):
        return self.testapp.get(route, params=params, headers={"X-Secret-Key": self.SECRET_KEY})

    def post_authenticated(self, route, params=dict()):
        return self.testapp.post(route, params=params, headers={"X-Secret-Key": self.SECRET_KEY})

    def test_secret_validation(self):
        url_mapping = GermanyServer.URL_MAPPING
        for route, page in url_mapping:
            if "/get_" in route or route == '/':
                response = self.testapp.get(route)
                self.assertEqual(response.status_int, 200)
                self.assertEqual(response.normal_body, 'Secret Key is not valid')
                self.assertEqual(response.content_type, 'text/html')
            else:
                response = self.testapp.post(route)
                self.assertEqual(response.status_int, 200)
                self.assertEqual(response.normal_body, 'Secret Key is not valid')
                self.assertEqual(response.content_type, 'text/html')

    def test_token_adding(self):
        response = self.get_authenticated("/get_tokens")
        self.assertEqual(response.normal_body, '{"result": []}')

        response = self.post_authenticated("/add_token", params={"token": "MyToken"})
        self.assertEqual(response.normal_body, 'Added token successfully')
        response = self.get_authenticated("/get_tokens")
        self.assertEqual(response.normal_body, '{"result": ["MyToken"]}')

        response = self.post_authenticated("/add_token", params={"token": "MyToken"})
        self.assertEqual(response.normal_body, 'This token is already saved')
        response = self.get_authenticated("/get_tokens")
        self.assertEqual(response.normal_body, '{"result": ["MyToken"]}')

        response = self.post_authenticated("/add_token", params={"token": "MyToken2"})
        self.assertEqual(response.normal_body, 'Added token successfully')
        response = self.get_authenticated("/get_tokens")
        self.assertEqual(response.normal_body, '{"result": ["MyToken", "MyToken2"]}')


    def test_token_deleting(self):
        response = self.get_authenticated("/get_tokens")
        self.assertEqual(response.normal_body, '{"result": []}')

        response = self.post_authenticated("/add_token", params={"token": "MyToken"})
        self.assertEqual(response.normal_body, 'Added token successfully')
        response = self.post_authenticated("/add_token", params={"token": "MyToken2"})
        self.assertEqual(response.normal_body, 'Added token successfully')
        response = self.get_authenticated("/get_tokens")
        self.assertEqual(response.normal_body, '{"result": ["MyToken", "MyToken2"]}')

        response = self.post_authenticated("/delete_token", params={"token": "MyToken2"})
        self.assertEqual(response.normal_body, 'Deleted token successfully')
        response = self.get_authenticated("/get_tokens")
        self.assertEqual(response.normal_body, '{"result": ["MyToken"]}')

        response = self.post_authenticated("/delete_token", params={"token": "MyToken2"})
        self.assertEqual(response.normal_body, 'No token found')
        response = self.get_authenticated("/get_tokens")
        self.assertEqual(response.normal_body, '{"result": ["MyToken"]}')

        response = self.post_authenticated("/delete_token", params={"token": "MyToken"})
        self.assertEqual(response.normal_body, 'Deleted token successfully')
        response = self.get_authenticated("/get_tokens")
        self.assertEqual(response.normal_body, '{"result": []}')

    def test_filter_adding(self):
        response = self.get_authenticated("/get_filters")
        self.assertEqual(response.normal_body, '{"result": []}')

        response = self.post_authenticated("/add_filter", params={"userId": "1", "filterSetting": "all"})
        self.assertEqual(response.normal_body, 'Added filter successfully')
        response = self.get_authenticated("/get_filters")
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["userId"], "1")
        self.assertEqual(result[0]["filterSetting"], "all")

        response = self.post_authenticated("/add_filter", params={"userId": "1", "filterSetting": "schwedt"})
        self.assertEqual(response.normal_body, 'Filter was updated successfully')
        response = self.get_authenticated("/get_filters")
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["userId"], "1")
        self.assertEqual(result[0]["filterSetting"], "schwedt")

        response = self.post_authenticated("/add_filter", params={"userId": "2", "filterSetting": "schwedt"})
        self.assertEqual(response.normal_body, 'Added filter successfully')
        response = self.get_authenticated("/get_filters")
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["userId"], "1")
        self.assertEqual(result[0]["filterSetting"], "schwedt")
        self.assertEqual(result[1]["userId"], "2")
        self.assertEqual(result[1]["filterSetting"], "schwedt")

    def test_filter_deleting(self):
        response = self.get_authenticated("/get_filters")
        self.assertEqual(response.normal_body, '{"result": []}')

        response = self.post_authenticated("/add_filter", params={"userId": "1", "filterSetting": "all"})
        response = self.post_authenticated("/add_filter", params={"userId": "2", "filterSetting": "schwedt"})
        response = self.get_authenticated("/get_filters")
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["userId"], "1")
        self.assertEqual(result[0]["filterSetting"], "all")
        self.assertEqual(result[1]["userId"], "2")
        self.assertEqual(result[1]["filterSetting"], "schwedt")

        response = self.post_authenticated("/delete_filter", params={"userId": "1", "filterSetting": "all"})
        self.assertEqual(response.normal_body, 'Deleted filter successfully')
        response = self.get_authenticated("/get_filters")
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["userId"], "2")
        self.assertEqual(result[0]["filterSetting"], "schwedt")

        response = self.post_authenticated("/delete_filter", params={"userId": "1", "filterSetting": "all"})
        self.assertEqual(response.normal_body, 'No filter found')
        response = self.get_authenticated("/get_filters")
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["userId"], "2")
        self.assertEqual(result[0]["filterSetting"], "schwedt")

        response = self.post_authenticated("/delete_filter", params={"userId": "2", "filterSetting": "schwedt"})
        response = self.get_authenticated("/get_filters")
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 0)

    def test_protocol_adding(self):
        response = self.get_authenticated("/get_protocols")
        self.assertEqual(response.normal_body, '{"result": []}')

        response = self.post_authenticated("/add_protocol", params={"competitionParties": "MyParty"})
        self.assertEqual(response.normal_body, 'Added protocol successfully')
        response = self.get_authenticated("/get_protocols")
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["parties"], "MyParty")

        response = self.post_authenticated("/add_protocol", params={"competitionParties": "MyParty"})
        self.assertEqual(response.normal_body, 'This protocol is already saved')
        response = self.get_authenticated("/get_protocols")
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["parties"], "MyParty")

        response = self.post_authenticated("/add_protocol", params={"competitionParties": "MyParty2"})
        self.assertEqual(response.normal_body, 'Added protocol successfully')
        response = self.get_authenticated("/get_protocols")
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["parties"], "MyParty")
        self.assertEqual(result[1]["parties"], "MyParty2")

    def test_protocol_deleting(self):
        response = self.get_authenticated("/get_protocols")
        self.assertEqual(response.normal_body, '{"result": []}')

        response = self.post_authenticated("/add_protocol", params={"competitionParties": "MyParty"})
        self.assertEqual(response.normal_body, 'Added protocol successfully')
        response = self.post_authenticated("/add_protocol", params={"competitionParties": "MyParty2"})
        self.assertEqual(response.normal_body, 'Added protocol successfully')
        response = self.get_authenticated("/get_protocols")
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["parties"], "MyParty")
        self.assertEqual(result[1]["parties"], "MyParty2")

        response = self.post_authenticated("/delete_protocol", params={"competitionParties": "MyParty2"})
        self.assertEqual(response.normal_body, 'Deleted protocol successfully')
        response = self.get_authenticated("/get_protocols")
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["parties"], "MyParty")

        response = self.post_authenticated("/delete_protocol", params={"competitionParties": "MyParty2"})
        self.assertEqual(response.normal_body, 'No protocol found')
        response = self.get_authenticated("/get_protocols")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["parties"], "MyParty")

        response = self.post_authenticated("/delete_protocol", params={"competitionParties": "MyParty"})
        self.assertEqual(response.normal_body, 'Deleted protocol successfully')
        response = self.get_authenticated("/get_protocols")
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 0)

    def test_adding_articles(self):
        response = self.get_authenticated("/get_articles")
        self.assertEqual(response.normal_body, '{"result": []}')

        url = "http://gewichtheben.blauweiss65-schwedt.de/?page_id=6858&paged=1"
        date = "1456182000"
        heading = "My Article Ä"
        content = "My Content Ä"
        publisher = "My Publisher"
        params = {"url": url, "date": date, "heading": heading, "content": content, "publisher": publisher}
        response = self.post_authenticated("/add_article", params=params)
        self.assertEqual(response.normal_body, 'Added article successfully')
        response = self.get_authenticated("/get_articles")
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["url"], url)

        response = self.post_authenticated("/add_article", params=params)
        self.assertEqual(response.normal_body, 'This article is already saved')
        response = self.get_authenticated("/get_articles")
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["url"], url)

        params = {"url": url + "_2", "date": date, "heading": heading, "content": content, "publisher": publisher}
        response = self.post_authenticated("/add_article", params=params)
        self.assertEqual(response.normal_body, 'Added article successfully')
        response = self.get_authenticated("/get_articles")
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["url"], url)
        self.assertEqual(result[1]["url"], url + "_2")

    def test_deleting_articles(self):
        response = self.get_authenticated("/get_articles")
        self.assertEqual(response.normal_body, '{"result": []}')
        url = "http://gewichtheben.blauweiss65-schwedt.de/?page_id=6858&paged=1"
        date = "1456182000"
        heading = "My Article Ä"
        content = "My Content Ä"
        publisher = "My Publisher"
        params = {"url": url, "date": date, "heading": heading, "content": content, "publisher": publisher}
        response = self.post_authenticated("/add_article", params=params)
        params["url"] = url + "_2"
        response = self.post_authenticated("/add_article", params=params)
        response = self.get_authenticated("/get_articles")
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["url"], url)
        self.assertEqual(result[1]["url"], url + "_2")

        response = self.post_authenticated("/delete_article", params={"url": url})
        self.assertEqual(response.normal_body, 'Deleted article successfully')
        response = self.get_authenticated("/get_articles")
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["url"], url + "_2")

        response = self.post_authenticated("/delete_article", params={"url": url})
        self.assertEqual(response.normal_body, 'No article found')
        response = self.get_authenticated("/get_articles")
        result = json.loads(response.normal_body)["result"]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["url"], url + "_2")

        response = self.post_authenticated("/delete_article", params={"url": url + "_2"})
        self.assertEqual(response.normal_body, 'Deleted article successfully')
        response = self.get_authenticated("/get_articles")
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


if __name__ == '__main__':
    unittest.main()