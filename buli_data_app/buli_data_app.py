import json
import logging
import webapp2
from google.appengine.ext import ndb
from server_utils import valid_secret_key, json_serial, json_deserial
from google.appengine.api import memcache

DEFAULT_RELAY_VALUE = 'default_relay'


def schedule_key(relay=DEFAULT_RELAY_VALUE):
    return ndb.Key('Schedule', relay)


def competition_key(relay=DEFAULT_RELAY_VALUE):
    return ndb.Key('Competitions', relay)


def table_key(relay=DEFAULT_RELAY_VALUE):
    return ndb.Key('Table', relay)


class Schedule(ndb.Model):
    """A schedule for competitions for a relay"""
    json_value = ndb.StringProperty(indexed=False)


class Competitions(ndb.Model):
    """Held competitions for a relay"""
    json_value = ndb.StringProperty(indexed=False)


class Table(ndb.Model):
    """A table about club placements for a relay"""
    json_value = ndb.StringProperty(indexed=False)


def add_schedule_to_cache(relay, schedule_dict):
    if not memcache.add('{}:schedule'.format(relay), json.dumps(schedule_dict, default=json_serial), time=60 * 60 * 24 * 7):
        logging.error('Memcache set failed for schedule ' + relay)


def add_competition_to_cache(relay, competition_dict):
    if not memcache.add('{}:competitions'.format(relay), json.dumps(competition_dict, default=json_serial), time=60 * 60 * 24 * 7):
        logging.error('Memcache set failed for competition ' + relay)


def add_table_to_cache(relay, table_dict):
    if not memcache.add('{}:table'.format(relay), json.dumps(table_dict, default=json_serial), time=60 * 60 * 24 * 7):
        logging.error('Memcache set failed for table ' + relay)


class SetSchedule(webapp2.RequestHandler):
    def post(self):
        if valid_secret_key(self.request):
            json_value = json.loads(self.request.body, encoding="utf-8")
            relay = json.loads(json_value)["relay"]
            schedule_query = Schedule.query(ancestor=schedule_key(relay))
            schedules = schedule_query.fetch(100)
            for schedule in schedules:
                schedule.key.delete()
            schedule = Schedule(parent=schedule_key(relay))
            schedule.json_value = json_value
            schedule.put()
            add_schedule_to_cache(relay, schedule.to_dict())
            self.response.write('Updated schedule successfully')
        else:
            self.response.out.write('Secret Key is not valid')


class GetSchedule(webapp2.RequestHandler):
    def get(self):
        if valid_secret_key(self.request):
            relay = self.request.get("relay")
            schedule_json = memcache.get('{}:schedule'.format(relay))
            if schedule_json is None:
                schedule_query = Schedule.query(ancestor=schedule_key(relay))
                schedules = schedule_query.fetch(100)
                if len(schedules) > 0:
                    self.response.write(schedules[0].json_value)
                else:
                    self.response.write('No schedule found')
            else:
                schedule = Schedule(**json.loads(schedule_json, object_pairs_hook=json_deserial))
                schedule_dict = json.loads(schedule.json_value)
                self.response.write(json.dumps(schedule_dict, encoding='utf-8'))
        else:
            self.response.out.write('Secret Key is not valid')


class SetCompetitions(webapp2.RequestHandler):
    def post(self):
        if valid_secret_key(self.request):
            json_value = json.loads(self.request.body, encoding="utf-8")
            relay = json.loads(json_value)["relay"]
            competition_query = Competitions.query(ancestor=competition_key(relay))
            competitions = competition_query.fetch(100)
            for competition in competitions:
                competition.key.delete()
            competition = Competitions(parent=competition_key(relay))
            competition.json_value = json_value
            competition.put()
            add_competition_to_cache(relay, competition.to_dict())
            self.response.write('Updated competitions successfully')
        else:
            self.response.out.write('Secret Key is not valid')


class GetCompetitions(webapp2.RequestHandler):
    def get(self):
        if valid_secret_key(self.request):
            relay = self.request.get("relay")
            competitions_json = memcache.get('{}:competitions'.format(relay))
            if competitions_json is None:
                competition_query = Competitions.query(ancestor=competition_key(relay))
                competitions = competition_query.fetch(100)
                if len(competitions) > 0:
                    self.response.write(competitions[0].json_value)
                else:
                    self.response.write('No competitions found')
            else:
                competition = Competitions(**json.loads(competitions_json, object_pairs_hook=json_deserial))
                competition_dict = json.loads(competition.json_value)
                self.response.write(json.dumps(competition_dict, encoding='utf-8'))
        else:
            self.response.out.write('Secret Key is not valid')


class SetTable(webapp2.RequestHandler):
    def post(self):
        if valid_secret_key(self.request):
            json_value = json.loads(self.request.body, encoding="utf-8")
            relay = json.loads(json_value)["relay"]
            table_query = Table.query(ancestor=table_key(relay))
            tables = table_query.fetch(100)
            for table in tables:
                table.key.delete()
            table = Table(parent=table_key(relay))
            table.json_value = json_value
            table.put()
            add_table_to_cache(relay, table.to_dict())
            self.response.write('Updated table successfully')
        else:
            self.response.out.write('Secret Key is not valid')


class GetTable(webapp2.RequestHandler):
    def get(self):
        if valid_secret_key(self.request):
            relay = self.request.get("relay")
            table_json = memcache.get('{}:table'.format(relay))
            if table_json is None:
                table_query = Table.query(ancestor=table_key(relay))
                tables = table_query.fetch(100)
                if len(tables) > 0:
                    self.response.write(tables[0].json_value)
                else:
                    self.response.write('No table found')
            else:
                table = Table(**json.loads(table_json, object_pairs_hook=json_deserial))
                table_dict = json.loads(table.json_value)
                self.response.write(json.dumps(table_dict, encoding='utf-8'))
        else:
            self.response.out.write('Secret Key is not valid')


class MainPage(webapp2.RequestHandler):
    def get(self):
        if valid_secret_key(self.request):
            self.response.out.write('Valid Secret Key - nice!')
        else:
            self.response.out.write('Secret Key is not valid')


class BuliDataServer():
    URL_MAPPING = [('/', MainPage),
                   ('/set_schedule', SetSchedule),
                   ('/get_schedule', GetSchedule),
                   ('/set_competitions', SetCompetitions),
                   ('/get_competitions', GetCompetitions),
                   ('/set_table', SetTable),
                   ('/get_table', GetTable),
                   ]

    def start(self):
        return webapp2.WSGIApplication(self.URL_MAPPING, debug=False)


server = BuliDataServer()
app = server.start()
