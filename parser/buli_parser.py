#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
import codecs
import ConfigParser
import json
import os
import re
import requests
import urllib2
from utils import get_endpoint

ENDPOINT = get_endpoint()

if os.path.isfile("config.ini"):
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.read('config.ini')
    APPSPOT_KEY = config.get("appspot", "X-Secret-Key")


class BuliParser:
    def __init__(self, season, league, relay, push_descr, fragment_id):
        self.league = league
        self.relay = relay
        self.iat_season_base = "https://www.iat.uni-leipzig.de/datenbanken/blgew{0}/".format(season)
        self.iat_schedule_url = "{0}start.php?pid=%27123%27&ansetzungen=1&bl={1}&staffel={2}".format(self.iat_season_base, league, relay)
        self.iat_competitions_url = "{0}start.php?pid=%27123%27&resultate=1&bl={1}&staffel={2}".format(self.iat_season_base, league, relay)
        self.iat_table_url = "{0}start.php?pid=%27123%27&tabelle=1&bl={1}&staffel={2}".format(self.iat_season_base, league, relay)
        self.push_descr = push_descr
        self.fragment_id = fragment_id
        self.error_occured = False
        self.TIMEOUT = 15

    # Helper functions

    def get_additional_entries(self, old_array, new_array):
        new_entries = []
        for new_entry in new_array:
            if new_entry not in old_array:
                new_entries.append(new_entry)
        return new_entries

    def save_push_message(self, headline, message_array, fragment_sub_id):
        #TITLE#TEXT#DESCRIPTION#FRAGMENT_ID#FRAGMENT_SUB_ID
        #Neue Tabellenergebnisse#1. Potsdam|2.Berlin#2. Bundesliga - Staffel Nordost#5#2
        msg = headline + "#" + "|".join(message_array) + "#" + self.push_descr + "#" + self.fragment_id + "#" + fragment_sub_id + "\n"
        push_file = codecs.open('push_messages.txt', 'a', 'utf-8')
        push_file.write(msg)
        push_file.close()

    # Main functions


    def update_schedule(self):
        """Save scheduled competitions in schedule_file_name.json"""
        print "Parsing scheduled competitions ..."
        try:
            schedule_page = urllib2.urlopen(self.iat_schedule_url, timeout=self.TIMEOUT).read()
            if "</TABLE>" in schedule_page:
                scheduled = schedule_page.split("</TABLE>")[0]
            else:
                raise Exception('There is no table on this page.')
        except Exception, e:
            print 'Error while downloading schedule ', e
            self.error_occured = True
            return

        re_competition_entry = re.compile(ur'(?<=class=font4>).*(?=[\r\n]?<\/TD>)')
        schedule_entries = re.findall(re_competition_entry, scheduled.replace('</TD></TR>', '</TD>\n</TR>'))
        schedule_entries = [w.replace('\r', '').replace('<br>', ' ') for w in schedule_entries]

        schedule_dict = {}
        final_schedule = []

        for i in range(0, len(schedule_entries), 7):
            if schedule_entries[i+6] == "&nbsp;":
                entry = {}
                entry["date"] = schedule_entries[i]
                entry["home"] = schedule_entries[i+1]
                entry["guest"] = schedule_entries[i+2]
                entry["location"] = schedule_entries[i+3]
                entry["time"] = schedule_entries[i+4].split('/')[1].split(' ')[0]

                final_schedule.append(entry)

        schedule_dict["schedule"] = final_schedule
        schedule_dict["relay"] = self.league + self.relay
        self.send_post(json.dumps(schedule_dict), '/set_schedule')


    def update_competitions(self):
        """Save past competitions in competition_file_name.json"""
        print "Parsing past competitions ..."
        try:
            competitions_page = self.download_unicode(self.iat_competitions_url)
            if "</TABLE>" in competitions_page:
                competitions = competitions_page.split("</TABLE>")[0]
            else:
                raise Exception('There is no table on this page.')
        except Exception, e:
            print 'Error while downloading competitions ', e
            self.error_occured = True
            return

        re_competition_entry = re.compile(ur'(?<=class=font4>).*(?=[\r\n]?<\/TD>)')
        re_href = re.compile(ur'(?<=href=)[^>]*(?=>)')
        competition_entries = re.findall(re_competition_entry, competitions)
        competition_entries = [w.replace('\r', '').replace('<br>', ' ') for w in competition_entries]

        competitions_dict = {}
        final_competitions = []

        for i in range(0, len(competition_entries), 7):
            entry = {}
            entry["location"] = competition_entries[i+1]
            entry["date"] = competition_entries[i+2]
            entry["home"] = competition_entries[i+3]
            entry["guest"] = competition_entries[i+4]
            entry["score"] = competition_entries[i+5]
            entry["url"] = self.iat_season_base + re.findall(re_href, competition_entries[i+6])[0]

            final_competitions.append(entry)

        competitions_dict["competitions"] = final_competitions
        competitions_dict["relay"] = self.league + self.relay
        self.send_post(json.dumps(competitions_dict), '/set_competitions')


    def update_table(self):
        """Save table entries in table_file_name.json"""
        print "Parsing table ..."
        try:
            table_page = self.download_unicode(self.iat_table_url)
            if "</TABLE>" in table_page:
                table = table_page.split("</TABLE>")[0]
            else:
                raise Exception('There is no table on this page.')
        except Exception, e:
            print 'Error while downloading table ', e
            self.error_occured = True
            return

        re_table_entry = re.compile(ur'(?<=class=font4>).*(?=[\r\n]?<\/TD>)')
        table_entries = re.findall(re_table_entry, table)
        table_entries = [w.replace('\r', '') for w in table_entries]

        table_dict = {}
        final_entries = []

        for i in range(0, len(table_entries), 4):
            entry = {}
            entry["place"] = str(i/4+1)
            entry["club"] = table_entries[i]
            entry["score"] = table_entries[i+1]
            entry["max_score"] = table_entries[i+2]
            entry["cardinal_points"] = table_entries[i+3]
            final_entries.append(entry)

        table_dict["table"] = final_entries
        table_dict["relay"] = self.league + self.relay
        self.send_post(json.dumps(table_dict), '/set_table')

    def create_buli_files(self):
        print "Creating Bundesliga files for BL " + self.league + " - " + self.relay
        for func in [self.update_schedule, self.update_competitions, self.update_table]:
            if not self.error_occured:
                func()

    def send_post(self, payload, path):
        r = requests.post(ENDPOINT + path, json=payload, headers={"X-Secret-Key": APPSPOT_KEY})
        return r.content

    def download_unicode(self, url):
        req = urllib2.urlopen(url, timeout=self.TIMEOUT)
        encoding = req.headers['content-type'].split('charset=')[-1]
        return unicode(req.read(), encoding).encode("utf-8")