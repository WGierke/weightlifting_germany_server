import json
import os
import time
import webapp2
import yaml
import urllib
from google.appengine.ext import ndb
from datetime import datetime

DEFAULT_RELAY_VALUE = 'default_relay'
DEFAULT_TOKEN_VALUE = 'default_token'
DEFAULT_USER_ID = 'default_user'
DEFAULT_FILTER_VALUE = 'default_filter'
DEFAULT_PARTIES_VALUES = 'default_parties'
DEFAULT_URL_VALUE = 'default_url'


if os.environ.get("SECRET_KEY"):
    SECRET_KEY = os.environ.get("SECRET_KEY")
else:
    with open('germany_app_engine/app.yaml') as f:
        SECRET_KEY = yaml.load(f)["env_variables"]["SECRET_KEY"]


# Key methods


def schedule_key(relay=DEFAULT_RELAY_VALUE):
    return ndb.Key('Schedule', relay)


def competition_key(relay=DEFAULT_RELAY_VALUE):
    return ndb.Key('Competition', relay)


def table_value(relay=DEFAULT_RELAY_VALUE):
    return ndb.Key('Table', relay)


def token_key(token_value=DEFAULT_TOKEN_VALUE):
    return ndb.Key('Token', token_value)


def filter_key(user_id=DEFAULT_USER_ID):
    return ndb.Key('Filter', user_id)


def protocol_key(parties=DEFAULT_PARTIES_VALUES):
    return ndb.Key('SharedProtocol', parties)


def article_key(url=DEFAULT_URL_VALUE):
    return ndb.Key('Article', url)


# Helper methods


def valid_secret_key(request):
    return 'X-Secret-Key' in request.headers and request.headers["X-Secret-Key"] == SECRET_KEY


# Models

class Schedule(ndb.Model):
    """A scheduled competition"""
    date = ndb.StringProperty(indexed=True)
    time = ndb.StringProperty(indexed=False)
    home = ndb.StringProperty(indexed=False)
    guest = ndb.StringProperty(indexed=False)
    location = ndb.StringProperty(indexed=False)


class Competition(ndb.Model):
    """A competition that was held"""
    date = ndb.StringProperty(indexed=True)
    home = ndb.StringProperty(indexed=False)
    guest = ndb.StringProperty(indexed=False)
    location = ndb.StringProperty(indexed=False)
    score = ndb.StringProperty(indexed=False)
    url = ndb.StringProperty(indexed=False)


class Table(ndb.Model):
    """A table entry"""
    cardinal_points = ndb.StringProperty(indexed=False)
    club = ndb.StringProperty(indexed=False)
    max_score = ndb.StringProperty(indexed=False)
    place = ndb.StringProperty(indexed=False)
    score = ndb.StringProperty(indexed=False)


class Token(ndb.Model):
    """A GCM token to send the app users push notifications"""
    value = ndb.StringProperty(indexed=False)


class FilterSetting(ndb.Model):
    """Club/Relay a user uses as filter"""
    user_id = ndb.StringProperty(indexed=False)
    filter_setting = ndb.StringProperty(indexed=False)
    timestamp = ndb.DateTimeProperty(auto_now=True)


class SharedProtocol(ndb.Model):
    """Protocol that was shared"""
    competition_parties = ndb.StringProperty(indexed=False)
    timestamp = ndb.DateTimeProperty(auto_now=True)


class Article(ndb.Model):
    """A published article about German weightlifting"""
    url = ndb.StringProperty(indexed=True)
    publisher = ndb.StringProperty(indexed=True)
    heading = ndb.StringProperty(indexed=False)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now=False)
    image = ndb.StringProperty(indexed=False)

# Pages


class MainPage(webapp2.RequestHandler):
    def get(self):
        if valid_secret_key(self.request):
            self.response.out.write('Valid Secret Key - nice!')
        else:
            self.response.out.write('Secret Key is not valid')


class SetSchedules(webapp2.RequestHandler):
    def post(self):
        if valid_secret_key(self.request):
            #print self.request.body
            competitions = json.loads(self.request.body, encoding="utf-8")
            competitions = json.loads(competitions)
            print competitions["past_competitions"][0]
            self.response.write("no")
        #     value = self.request.get('token')
        #     token_query = Token.query(ancestor=token_key(value))
        #     tokens = token_query.fetch(100)
        #     if len(tokens) == 0:
        #         token = Token(parent=token_key(value))
        #         token.value = value
        #         token.put()
        #         self.response.write('Added token successfully')
        #     else:
        #         self.response.write('This token is already saved')
        else:
            self.response.out.write('Secret Key is not valid')



class GetSchedules(webapp2.RequestHandler):
    def post(self):
        if valid_secret_key(self.request):
            relay = self.request.get("relay")
            schedule_query = Schedule.query(ancestor=schedule_key(relay))
            schedules = schedule_query.fetch(200)
            result = []
            for schedule in schedules:
                result.append({"date": schedule.date, "time": schedule.time,
                               "home": schedule.home, "guest": schedule.guest,
                               "location": schedule.location})
            response_dict = {"scheduled_competitions": result}
            self.response.write(json.dumps(response_dict, encoding='utf-8'))
        else:
            self.response.out.write('Secret Key is not valid')


class GetTokens(webapp2.RequestHandler):
    def get(self):
        if valid_secret_key(self.request):
            token_query = Token.query()
            tokens = token_query.fetch(1000)
            response_dict = {"result": map(lambda (x): x.value, tokens)}
            self.response.write(json.dumps(response_dict, encoding='latin1'))
        else:
            self.response.out.write('Secret Key is not valid')


class AddToken(webapp2.RequestHandler):
    def post(self):
        if valid_secret_key(self.request):
            value = self.request.get('token')
            token_query = Token.query(ancestor=token_key(value))
            tokens = token_query.fetch(100)
            if len(tokens) == 0:
                token = Token(parent=token_key(value))
                token.value = value
                token.put()
                self.response.write('Added token successfully')
            else:
                self.response.write('This token is already saved')
        else:
            self.response.out.write('Secret Key is not valid')


class DeleteToken(webapp2.RequestHandler):
    def post(self):
        if valid_secret_key(self.request):
            value = self.request.get('token')
            token_query = Token.query(ancestor=token_key(value))
            tokens = token_query.fetch(100)
            if len(tokens) > 0:
                for token in tokens:
                    token.key.delete()
                self.response.write('Deleted token successfully')
            else:
                self.response.write('No token found')
        else:
            self.response.out.write('Secret Key is not valid')


class GetFilters(webapp2.RequestHandler):
    def get(self):
        if valid_secret_key(self.request):
            filter_query = FilterSetting.query()
            filters = filter_query.fetch(1000)
            filter_array = []
            for filter_entity in filters:
                filter_dict = {"userId": filter_entity.user_id, "createdAt": filter_entity.timestamp.strftime("%s"),
                               "filterSetting": filter_entity.filter_setting}
                filter_array.append(filter_dict)
            response_dict = {"result": filter_array}
            self.response.write(json.dumps(response_dict, encoding='latin1'))
        else:
            self.response.out.write('Secret Key is not valid')


class AddFilter(webapp2.RequestHandler):
    def post(self):
        if valid_secret_key(self.request):
            user_id = self.request.get('userId')
            filter_setting = self.request.get('filterSetting')
            filter_query = FilterSetting.query(ancestor=filter_key(user_id))
            filters = filter_query.fetch(100)
            if len(filters) == 0:
                filter_entity = FilterSetting(parent=filter_key(user_id))
                filter_entity.filter_setting = filter_setting
                filter_entity.user_id = user_id
                filter_entity.put()
                self.response.write('Added filter successfully')
            else:
                for filter_entity in filters:
                    filter_entity.filter_setting = filter_setting
                    filter_entity.user_id = user_id
                    filter_entity.put()
                    self.response.write('Filter was updated successfully')
        else:
            self.response.out.write('Secret Key is not valid')


class DeleteFilter(webapp2.RequestHandler):
    def post(self):
        if valid_secret_key(self.request):
            user_id = self.request.get('userId')
            filter_query = FilterSetting.query(ancestor=filter_key(user_id))
            filter_settings = filter_query.fetch(100)
            if len(filter_settings) > 0:
                for filter_entity in filter_settings:
                    filter_entity.key.delete()
                self.response.write('Deleted filter successfully')
            else:
                self.response.write('No filter found')
        else:
            self.response.out.write('Secret Key is not valid')


class GetSharedProtocols(webapp2.RequestHandler):
    def get(self):
        if valid_secret_key(self.request):
            protocol_query = SharedProtocol.query()
            shared_protocols = protocol_query.fetch(1000)
            protocol_array = []
            for protocol_entity in shared_protocols:
                protocol_dict = {"parties": protocol_entity.competition_parties,
                                 "createdAt": protocol_entity.timestamp.strftime("%s")}
                protocol_array.append(protocol_dict)
            response_dict = {"result": protocol_array}
            self.response.write(json.dumps(response_dict, encoding='latin1'))
        else:
            self.response.out.write('Secret Key is not valid')


class AddSharedProtocol(webapp2.RequestHandler):
    def post(self):
        if valid_secret_key(self.request):
            competition_parties = self.request.get('competitionParties')
            protocol_query = SharedProtocol.query(ancestor=protocol_key(competition_parties))
            protocols = protocol_query.fetch(100)
            if len(protocols) == 0:
                protocol_entity = SharedProtocol(parent=protocol_key(competition_parties))
                protocol_entity.competition_parties = competition_parties
                protocol_entity.put()
                self.response.write('Added protocol successfully')
            else:
                self.response.write('This protocol is already saved')
        else:
            self.response.out.write('Secret Key is not valid')


class DeleteSharedProtocol(webapp2.RequestHandler):
    def post(self):
        if valid_secret_key(self.request):
            competition_parties = self.request.get('competitionParties')
            protocol_query = SharedProtocol.query(ancestor=protocol_key(competition_parties))
            protocols = protocol_query.fetch(100)
            if len(protocols) > 0:
                for protocol_entity in protocols:
                    protocol_entity.key.delete()
                self.response.write('Deleted protocol successfully')
            else:
                self.response.write('No protocol found')
        else:
            self.response.out.write('Secret Key is not valid')


class GetArticles(webapp2.RequestHandler):
    def get(self):
        if valid_secret_key(self.request):
            article_query = Article.query()
            articles = article_query.fetch(1000)
            article_array = []
            for article_entity in articles:
                article_dict = {"url": article_entity.url}
                article_array.append(article_dict)
            response_dict = {"result": article_array}
            self.response.write(json.dumps(response_dict, encoding='latin1'))
        else:
            self.response.out.write('Secret Key is not valid')


class GetArticle(webapp2.RequestHandler):
    def get(self):
        if valid_secret_key(self.request):
            url = self.request.get("url")
            article_query = Article.query(ancestor=article_key(url))
            articles = article_query.fetch(100)
            if len(articles) > 0:
                article = articles[0]
                result = {"url": article.url, "date": str(time.mktime(article.date.timetuple())), 
                          "heading": article.heading, "publisher": article.publisher,
                          "content": article.content, "image": article.image}
                response_dict = {"result": result}
                self.response.write(json.dumps(response_dict, encoding='utf-8'))
            else:
                self.response.write('No article found')
        else:
            self.response.out.write('Secret Key is not valid')


class AddArticle(webapp2.RequestHandler):
    def post(self):
        if valid_secret_key(self.request):
            url = self.request.get("url")
            article_query = Article.query(ancestor=article_key(url))
            articles = article_query.fetch(100)
            if len(articles) == 0:
                article_entity = Article(parent=article_key(url))
                article_entity.url = url
                article_entity.publisher = self.request.get('publisher')
                article_entity.heading = self.request.get('heading')
                article_entity.content = self.request.get('content')
                article_entity.image = self.request.get('image')
                date = self.request.get('date')
                article_entity.date = datetime.fromtimestamp(float(date))
                article_entity.put()
                self.response.write('Added article successfully')
            else:
                self.response.write('This article is already saved')
        else:
            self.response.out.write('Secret Key is not valid')


class DeleteArticle(webapp2.RequestHandler):
    def post(self):
        if valid_secret_key(self.request):
            url = self.request.get('url')
            article_query = Article.query(ancestor=article_key(url))
            articles = article_query.fetch(100)
            if len(articles) > 0:
                for article_entity in articles:
                    article_entity.key.delete()
                self.response.write('Deleted article successfully')
            else:
                self.response.write('No article found')
        else:
            self.response.out.write('Secret Key is not valid')


class ArticleExists(webapp2.RequestHandler):
    def post(self):
        if valid_secret_key(self.request):
            url = self.request.get("url")
            article_query = Article.query(ancestor=article_key(url))
            articles = article_query.fetch(100)
            if len(articles) > 0:
                self.response.write('Yes')
            else:
                self.response.write('No')
        else:
            self.response.out.write('Secret Key is not valid')


class GermanyServer():
    URL_MAPPING = [('/', MainPage),
                   ('/get_schedules', GetSchedules),
                   ('/set_schedules', SetSchedules),

                   ('/add_token', AddToken),
                   ('/delete_token', DeleteToken),
                   ('/get_tokens', GetTokens),

                   ('/add_filter', AddFilter),
                   ('/delete_filter', DeleteFilter),
                   ('/get_filters', GetFilters),

                   ('/add_protocol', AddSharedProtocol),
                   ('/delete_protocol', DeleteSharedProtocol),
                   ('/get_protocols', GetSharedProtocols),

                   ('/add_article', AddArticle),
                   ('/delete_article', DeleteArticle),
                   ('/get_articles', GetArticles),
                   ('/get_article', GetArticle),
                   ('/article_exists', ArticleExists),
                   ]
    def start(self):
        return webapp2.WSGIApplication(self.URL_MAPPING, debug=True)

server = GermanyServer()
app = server.start()