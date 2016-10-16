#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
import codecs
import ConfigParser
import json
import os
import re
import requests
import urllib2
from utils import get_endpoint, notify_users, read_json, write_json, write_news

ENDPOINT = get_endpoint()

if os.path.isfile("config.ini"):
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.read('config.ini')
    APPSPOT_KEY = config.get("appspot", "X-Secret-Key")


class BuliParser:
    def __init__(self, season, league, relay, push_descr, fragment_id, leage_relay="LEAGUE_RELAY"):
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
        self.schedule_file_name = "data/r{}_{}_schedule.json".format(season, leage_relay)
        self.competition_file_name = "data/r{}_{}_competitions.json".format(season, leage_relay)
        self.table_file_name = "data/r{}_{}_table.json".format(season, leage_relay)

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

    def generate_schedule_json_from_url(self, url):
        print "Parsing scheduled competitions ..."
        try:
            schedule_page = urllib2.urlopen(url, timeout=self.TIMEOUT).read()
            if "</TABLE>" in schedule_page:
                scheduled = schedule_page.split("</TABLE>")[0]
            else:
                raise Exception('There is no table on this page.')
        except Exception, e:
            print 'Error while downloading schedule ', e
            self.error_occured = True
            schedule_dict = {"schedule": [], "relay": self.league + self.relay}
            return json.dumps(schedule_dict)

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
        return json.dumps(schedule_dict, sort_keys=True, indent=4, separators=(',', ': '), encoding='latin1')

    def update_schedule(self):
        new_schedule_json = self.generate_schedule_json_from_url(self.iat_schedule_url)
        if not os.path.isfile(self.schedule_file_name):
            write_json(self.schedule_file_name, new_schedule_json)
            return
        old_schedule_json = read_json(self.schedule_file_name)
        new_schedule_dict = json.loads(new_schedule_json)
        if sorted(new_schedule_json.decode("utf-8")) == sorted(old_schedule_json.decode("utf-8")):
            print "Local check: Schedule of " + new_schedule_dict["relay"] + " did not change"
            return
        else:
            print "Local check: Schedule of " + new_schedule_dict["relay"] + " changed"
            self.send_post(new_schedule_json, '/set_schedule')
            write_json(self.schedule_file_name, new_schedule_json)
            write_news("Updated schedule of " + new_schedule_dict["relay"])

    def generate_competitions_json_from_url(self, url):
        print "Parsing past competitions ..."
        try:
            competitions_page = self.download_unicode(url)
            if "</TABLE>" in competitions_page:
                competitions = competitions_page.split("</TABLE>")[0]
            else:
                raise Exception('There is no table on this page.')
        except Exception, e:
            print 'Error while downloading competitions ', e
            self.error_occured = True
            competitions_dict = {"competitions": [], "relay": self.league + self.relay}
            return json.dumps(competitions_dict)

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
        return json.dumps(competitions_dict, sort_keys=True, indent=4, separators=(',', ': '), encoding='latin1')

    def update_competitions(self):
        new_competitions_json = self.generate_competitions_json_from_url(self.iat_competitions_url)
        old_competitions_json = read_json(self.competition_file_name)
        if not os.path.isfile(self.competition_file_name):
            write_json(self.competition_file_name, new_competitions_json)
            return
        #new_competitions_json = '{"competitions": [{"date": "07.05.2016", "home": "TB 03 Roding", "guest": "AV Speyer 03", "location": "Roding", "score": "562.1 : 545.0 :562.0", "url": "https://www.iat.uni-leipzig.de/datenbanken/blgew1516/start.php?pid=' + "'123'" +  '&protokoll=1&wkid=E3714956BFC24D6798DCD9C94B0620CC"}],"relay": "1Gruppe+A"}'
        new_competitions_dict = json.loads(new_competitions_json)
        if sorted(new_competitions_json.decode("utf-8")) == sorted(old_competitions_json.decode("utf-8")):
            print "Local check: Competitions of " + new_competitions_dict["relay"] + " did not change"
            return
        else:
            print "Local check: Competitions of " + new_competitions_dict["relay"] + " changed"
            self.notify_users_about_new_competitions(new_competitions_json, old_competitions_json)
            write_json(self.competition_file_name, new_competitions_json)

    def notify_users_about_new_competitions(self, new_competitions_json, old_competitions_json):
        self.send_post(new_competitions_json, '/set_competitions')
        old_competitions_dict = json.loads(old_competitions_json, encoding='utf-8')["competitions"]
        new_competitions_dict = json.loads(new_competitions_json, encoding='utf-8')["competitions"]
        messages = []
        for competition in self.get_additional_entries(old_competitions_dict, new_competitions_dict):
            message = competition["home"] + " vs. " + competition["guest"] + " - " + competition["score"]
            print "Notifying user about " + message
            messages.append(message)
            write_news(message)
        notify_users("Neue Wettkampfergebnisse",
                     "|".join(messages),
                     self.push_descr,
                     self.fragment_id,
                     1)

    def generate_table_json_from_url(self, url):
        print "Parsing table ..."
        try:
            table_page = self.download_unicode(url)
            if "</TABLE>" in table_page:
                table = table_page.split("</TABLE>")[0]
            else:
                raise Exception('There is no table on this page.')
        except Exception, e:
            print 'Error while downloading table ', e
            self.error_occured = True
            table_dict = {"table": [], "relay": self.league + self.relay}
            return json.dumps(table_dict)

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
        return json.dumps(table_dict, sort_keys=True, indent=4, separators=(',', ': '), encoding='latin1')

    def update_table(self):
        new_table_json = self.generate_table_json_from_url(self.iat_table_url)
        old_table_json = read_json(self.table_file_name)
        if not os.path.isfile(self.table_file_name):
            write_json(self.table_file_name, new_table_json)
            return
        #new_table_json = '{"table": [{"cardinal_points": "18 : 0","club": "AV Speyer 03","max_score": "898.6","place": "1","score": "5056.2 : 4170.6"}],"relay": "1Gruppe+A"}'
        new_table_dict = json.loads(new_table_json)
        if sorted(new_table_json.decode("utf-8")) == sorted(old_table_json.decode("utf-8")):
            print "Local check: Table of " + new_table_dict["relay"] + " did not change"
            return
        else:
            print "Local check: Table of " + new_table_dict["relay"] + " changed"
            self.notify_users_about_new_placements(new_table_json, old_table_json)
            write_json(self.table_file_name, new_table_json)

    def notify_users_about_new_placements(self, new_table_json, old_table_json):
        self.send_post(new_table_json, '/set_table')
        old_table_dict = json.loads(old_table_json, encoding='utf-8')["table"]
        new_table_dict = json.loads(new_table_json, encoding='utf-8')["table"]
        messages = []
        for table_entry in self.get_additional_entries(old_table_dict, new_table_dict):
            print "Notifying user about " + table_entry["place"] + ". " + table_entry["club"]
            message = table_entry["place"] + ". " + table_entry["club"]
            messages.append(message)
            write_news(message)
        notify_users("Neue Tabellenergebnisse",
                     "|".join(messages),
                     self.push_descr,
                     self.fragment_id,
                     2)

    def update_buli(self):
        print "Updating Bundesliga records for BL " + self.league + " - " + self.relay
        for func in [self.update_schedule, self.update_competitions, self.update_table]:
            if not self.error_occured:
                func()

    def send_post(self, payload, path):
        r = requests.post(ENDPOINT + path, json=payload, headers={"X-Secret-Key": APPSPOT_KEY})
        return r.content

    def download_unicode(self, url):
        req = urllib2.urlopen(url, timeout=self.TIMEOUT)
        encoding = req.headers['content-type'].split('charset=')[-1]
        return unicode(req.read(), encoding)
