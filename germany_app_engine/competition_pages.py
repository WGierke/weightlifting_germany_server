import json
import webapp2
from google.appengine.ext import ndb
from utils import valid_secret_key

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
            self.response.write('Updated schedule successfully')
        else:
            self.response.out.write('Secret Key is not valid')


class GetSchedule(webapp2.RequestHandler):
    def get(self):
        if valid_secret_key(self.request):
            relay = self.request.get("relay")
            schedule_query = Schedule.query(ancestor=schedule_key(relay))
            schedules = schedule_query.fetch(100)
            if len(schedules) > 0:
                schedule = schedules[0]
                response_dict = {"result": schedule.json_value}
                self.response.write(json.dumps(response_dict, encoding='utf-8'))
            else:
                self.response.write('No schedule found')
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
            self.response.write('Updated competitions successfully')
        else:
            self.response.out.write('Secret Key is not valid')


class GetCompetitions(webapp2.RequestHandler):
    def get(self):
        if valid_secret_key(self.request):
            relay = self.request.get("relay")
            competition_query = Competitions.query(ancestor=competition_key(relay))
            competitions = competition_query.fetch(100)
            if len(competitions) > 0:
                competition = competitions[0]
                response_dict = {"result": competition.json_value}
                self.response.write(json.dumps(response_dict, encoding='utf-8'))
            else:
                self.response.write('No competitions found')
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
            self.response.write('Updated table successfully')
        else:
            self.response.out.write('Secret Key is not valid')


class GetTable(webapp2.RequestHandler):
    def get(self):
        if valid_secret_key(self.request):
            relay = self.request.get("relay")
            table_query = Table.query(ancestor=table_key(relay))
            tables = table_query.fetch(100)
            if len(tables) > 0:
                table = tables[0]
                response_dict = {"result": table.json_value}
                self.response.write(json.dumps(response_dict, encoding='utf-8'))
            else:
                self.response.write('No table found')
        else:
            self.response.out.write('Secret Key is not valid')
