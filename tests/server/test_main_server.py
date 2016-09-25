#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import unittest
import webtest
import yaml

from google.appengine.ext import testbed
from main_app.main_app import GermanyServer


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
            with open('main_app/app.yaml') as f: 
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


class TokenValidationServerTestCase(ServerTestCase):
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
