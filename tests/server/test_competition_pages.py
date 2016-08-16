#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
from test_server import ServerTestCase


class CompetitionServerTestCase(ServerTestCase):
    def test_schedule_setting(self):
        response = self.get_authenticated("/get_schedule?relay=2South")
        self.assertEqual(response.normal_body, 'No schedule found')

        params = {"relay": "2South", "schedule": [
                  {"date": "19.03.2016",
                   "guest": u"Meißen",
                   "home": "SV Germania Obrigheim",
                   "location": "Obrigheim"
                   }]}
        response = self.post_authenticated_json("/set_schedule", json=json.dumps(json.dumps(params)))
        response = self.get_authenticated("/get_schedule?relay=2South")
        result = json.loads(response.normal_body)["result"]
        result = json.loads(result)
        self.assertEqual(result["relay"], "2South")
        self.assertEqual(result["schedule"][0]["guest"], u"Meißen")

    def test_competitions_setting(self):
        response = self.get_authenticated("/get_competitions?relay=2South")
        self.assertEqual(response.normal_body, 'No competitions found')

        params = {"relay": "2South", "competitions": [
                  {"date": "19.03.2016",
                   "guest": u"Meißen",
                   "home": "SV Germania Obrigheim",
                   "location": "Obrigheim",
                   "score": "850.2 : 800.9",
                   "url": "https://www.iat.uni-leipzig.de/datenbanken/blgew1516/start.php?pid='123'&protokoll=1&wkid=7659C155B6CD48639ED93E8B3E2CCBB2"
                   }]}
        response = self.post_authenticated_json("/set_competitions", json=json.dumps(json.dumps(params)))
        response = self.get_authenticated("/get_competitions?relay=2South")
        result = json.loads(response.normal_body)["result"]
        result = json.loads(result)
        self.assertEqual(result["relay"], "2South")
        self.assertEqual(result["competitions"][0]["guest"], u"Meißen")

    def test_table_setting(self):
        response = self.get_authenticated("/get_table?relay=2South")
        self.assertEqual(response.normal_body, 'No table found')

        params = {"relay": "2South", "table": [
                  {"club": u"Münchener AC",
                   "max_score": u"100",
                   "score": u"100:200",
                   "place": u"1",
                   "cardinal_points": u"500"
                   }]}
        response = self.post_authenticated_json("/set_table", json=json.dumps(json.dumps(params)))
        response = self.get_authenticated("/get_table?relay=2South")
        result = json.loads(response.normal_body)["result"]
        result = json.loads(result)
        self.assertEqual(result["relay"], "2South")
        self.assertEqual(result["table"][0]["club"], u"Münchener AC")
