#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
import urllib2
import re
import os
import json
import codecs


class BuliParser:

    def __init__(self, season, league, relay, schedule_file_name, competition_file_name, table_file_name, push_descr, fragment_id):
        self.league = league
        self.relay = relay
        self.iat_season_base = "https://www.iat.uni-leipzig.de/datenbanken/blgew{0}/".format(season)
        self.iat_schedule_url = "{0}start.php?pid=%27123%27&ansetzungen=1&bl={1}&staffel={2}".format(self.iat_season_base, league, relay)
        self.iat_competitions_url = "{0}start.php?pid=%27123%27&resultate=1&bl={1}&staffel={2}".format(self.iat_season_base, league, relay)
        self.iat_table_url = "{0}start.php?pid=%27123%27&tabelle=1&bl={1}&staffel={2}".format(self.iat_season_base, league, relay)
        self.schedule_file_name = "data/" + schedule_file_name + ".json"
        self.competition_file_name = "data/" + competition_file_name + ".json"
        self.table_file_name = "data/" + table_file_name + ".json"
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


    def create_schedule_file(self):
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

        schedule_dict["scheduled_competitions"] = final_schedule
        json_scheduled = json.dumps(schedule_dict, encoding='latin1', sort_keys=True, indent=4, separators=(',', ': '))
        schedule_dict_json = "[" + json_scheduled + "]"

        if not os.path.isfile(self.schedule_file_name):
            with open(self.schedule_file_name, "w+") as f:
                f.write(schedule_dict_json.decode('utf-8'))
            return

        # Handle swapping of scheduled competitions due to IAT database
        with open(self.schedule_file_name, "r") as f:
            old_schedules = f.read()

        if sorted(schedule_dict_json.decode('utf-8')) != sorted(old_schedules.decode('utf-8')):
            print "Scheduled competitions: Change detected"
            f = open(self.schedule_file_name, "w")
            f.write(schedule_dict_json.decode('utf-8'))
            f.close()

            push_messages = []
            old_schedule_dict = json.loads(old_schedules, encoding='utf-8')[0]["scheduled_competitions"]
            new_schedule_dict = json.loads(schedule_dict_json, encoding='utf-8')[0]["scheduled_competitions"]

            additional_schedules = self.get_additional_entries(old_schedule_dict, new_schedule_dict)

            if(len(additional_schedules) > 0):
                for schedule in additional_schedules:
                    push_messages.append(schedule["home"] + " vs. " + schedule["guest"] + ": " + schedule["time"] + " in " + schedule["location"])
                self.save_push_message("Neue Ansetzungen", push_messages, "0")


    def create_competitions_file(self):
        """Save past competitions in competition_file_name.json"""
        print "Parsing past competitions ..."
        try:
            competitions_page = urllib2.urlopen(self.iat_competitions_url, timeout=self.TIMEOUT).read()
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

        competitions_dict["past_competitions"] = final_competitions
        json_competitions = json.dumps(competitions_dict, encoding='latin1', sort_keys=True, indent=4, separators=(',', ': '))
        competitions_dict_json = "[" + json_competitions + "]"

        if not os.path.isfile(self.competition_file_name):
            with open(self.competition_file_name, "w+") as f:
                f.write(competitions_dict_json.decode('utf-8'))
            return

        # Handle swapping of competitions due to IAT database
        with open(self.competition_file_name, "r") as f:
            old_competitions = f.read()

        if sorted(competitions_dict_json.decode('utf-8')) != sorted(old_competitions.decode('utf-8')):
            print "Competitions: Change detected"
            f = open(self.competition_file_name, "w")
            f.write(competitions_dict_json.decode('utf-8'))
            f.close()

            push_messages = []
            old_competitions_dict = json.loads(old_competitions, encoding='utf-8')[0]["past_competitions"]
            new_competitions_dict = json.loads(competitions_dict_json, encoding='utf-8')[0]["past_competitions"]

            for competition in self.get_additional_entries(old_competitions_dict, new_competitions_dict):
                push_messages.append(competition["home"] + " vs. " + competition["guest"] + " - " + competition["score"])
            self.save_push_message("Neue Wettkampfergebnisse", push_messages, "1")

    def create_table_file(self):
        """Save table entries in table_file_name.json"""
        print "Parsing table ..."
        try:
            table_page = urllib2.urlopen(self.iat_table_url, timeout=self.TIMEOUT).read()
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
        json_table = json.dumps(table_dict, encoding='latin1', sort_keys=True, indent=4, separators=(',', ': '))
        table_dict_json = "[" + json_table + "]"

        if not os.path.isfile(self.table_file_name):
            with open(self.table_file_name, "w+") as f:
                f.write(table_dict_json.decode('utf-8'))
            return

        with open(self.table_file_name, "r") as f:
            old_table = f.read()

        if sorted(old_table.decode('utf-8')) != sorted(table_dict_json.decode('utf-8')):
            f = open(self.table_file_name, "w")
            f.write(table_dict_json.decode('utf-8'))
            f.close()

            push_messages = []
            old_table_dict = json.loads(old_table, encoding='utf-8')[0]["table"]
            new_table_dict = json.loads(table_dict_json, encoding='utf-8')[0]["table"]

            for table_entry in self.get_additional_entries(old_table_dict, new_table_dict):
                push_messages.append(table_entry["place"] + ". " + table_entry["club"])
            self.save_push_message("Neue Tabellenergebnisse", push_messages, "2")

    def create_buli_files(self):
        print "Creating Bundesliga files for BL " + self.league + " - " + self.relay
        for func in [self.create_schedule_file, self.create_competitions_file, self.create_table_file]:
            if not self.error_occured:
                func()