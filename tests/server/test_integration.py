#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
from test_server import ServerTestCase
from parser.buli_parser import BuliParser

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
        self.assertEqual(table_dict["table"][-1]["club"], u"AC Meißen")
