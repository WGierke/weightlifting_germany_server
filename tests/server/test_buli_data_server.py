#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import os
import unittest
import webtest
import yaml

from google.appengine.ext import testbed
from parser.buli_parser import BuliParser
from buli_data_app.buli_data_app import BuliDataServer


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

        app = BuliDataServer().start()
        self.testapp = webtest.TestApp(app)

        # Load Secret Key
        if os.environ.get("SECRET_KEY"):
            self.SECRET_KEY = os.environ.get("SECRET_KEY")
        else:
            with open('buli_data_app/app.yaml') as f:
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

    def post_authenticated_json(self, route, json):
        return self.testapp.post(route, params=json, headers={"X-Secret-Key": self.SECRET_KEY}, content_type="application/json")

class CompetitionServerTestCase(ServerTestCase):

    def test_competitions_integration(self):
        BuliParser1B = BuliParser("1516", "1", "Gruppe+B", "1. Bundesliga - Gruppe B", "3")
        competitions_json = BuliParser1B.generate_competitions_json_from_url(BuliParser1B.iat_competitions_url)

        response = self.post_authenticated('/set_competitions', json.dumps(competitions_json))
        self.assertEqual(response.normal_body, 'Updated competitions successfully')

        response = self.get_authenticated('/get_competitions?relay=1Gruppe%2BB')
        competitions_dict = json.loads(response.normal_body)
        self.assertEqual(competitions_dict["relay"], "1Gruppe+B")
        self.assertEqual(len(competitions_dict["competitions"]), 22)
        self.assertEqual(competitions_dict["competitions"][0]["guest"], "AV Speyer 03")

    def test_tables_integration(self):
        BuliParser1B = BuliParser("1516", "1", "Gruppe+B", "1. Bundesliga - Gruppe B", "3")
        table_json = BuliParser1B.generate_table_json_from_url(BuliParser1B.iat_table_url)

        response = self.post_authenticated('/set_table', json.dumps(table_json))
        self.assertEqual(response.normal_body, 'Updated table successfully')

        response = self.get_authenticated('/get_table?relay=1Gruppe%2BB')
        table_dict = json.loads(response.normal_body)
        self.assertEqual(table_dict["relay"], "1Gruppe+B")
        self.assertEqual(len(table_dict["table"]), 7)
        #self.assertEqual(table_dict["table"][-1]["club"].encode("utf-8"), u'AC Mei\xdfen')
