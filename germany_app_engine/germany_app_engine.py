import json
import os

import webapp2
from google.appengine.ext import ndb
from datetime import datetime

DEFAULT_TOKEN_VALUE = 'default_token'
DEFAULT_USER_ID = 'default_user'
DEFAULT_FILTER_VALUE = 'default_filter'
DEFAULT_PARTIES_VALUES = 'default_parties'
DEFAULT_URL_VALUE = 'default_url'


# Key methods


def token_key(token_value=DEFAULT_TOKEN_VALUE):
    return ndb.Key('Token', token_value)


def filter_key(user_id=DEFAULT_USER_ID, filter_setting=DEFAULT_FILTER_VALUE):
    return ndb.Key('Filter', user_id + "-" + filter_setting)


def protocol_key(parties=DEFAULT_PARTIES_VALUES):
    return ndb.Key('SharedProtocol', parties)


def article_key(url=DEFAULT_URL_VALUE):
    return ndb.Key('Article', url)


# Helper methods


def valid_secret_key(request):
    return 'X-Secret-Key' in request.headers and request.headers["X-Secret-Key"] == os.environ.get("SECRET_KEY")


# Models


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

# Pages


class MainPage(webapp2.RequestHandler):
    def get(self):
        if valid_secret_key(self.request):
            self.response.out.write('Valid Secret Key - nice!')
        else:
            self.response.out.write('Secret Key is not valid')


class GetTokens(webapp2.RequestHandler):
    def get(self):
        if valid_secret_key(self.request):
            token_query = Token.query()
            tokens = token_query.fetch(1000)
            response_dict = {"result": map(lambda (x): x.value, tokens)}
            self.response.write(json.dumps(response_dict, encoding='latin1'))


class AddToken(webapp2.RequestHandler):
    def post(self):
        if valid_secret_key(self.request):
            value = self.request.get('token')
            token = Token(parent=token_key(value))
            token.value = value
            token.put()
            self.response.write('Success')


class DeleteToken(webapp2.RequestHandler):
    def post(self):
        if valid_secret_key(self.request):
            value = self.request.get('token')
            token_query = Token.query(ancestor=token_key(value))
            tokens = token_query.fetch(100)
            if len(tokens) > 0:
                for token in tokens:
                    token.key.delete()
                self.response.write('Success')
            else:
                self.response.write('No token found')


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


class AddFilter(webapp2.RequestHandler):
    def post(self):
        if valid_secret_key(self.request):
            user_id = self.request.get('userId')
            filter_setting = self.request.get('filterSetting')
            filter_entity = FilterSetting(parent=filter_key(user_id, filter_setting))
            filter_entity.filter_setting = filter_setting
            filter_entity.user_id = user_id
            filter_entity.put()
            self.response.write('Success')


class DeleteFilter(webapp2.RequestHandler):
    def post(self):
        if valid_secret_key(self.request):
            user_id = self.request.get('userId')
            filter_setting = self.request.get('filterSetting')
            filter_query = FilterSetting.query(ancestor=filter_key(user_id, filter_setting))
            filter_settings = filter_query.fetch(100)
            if len(filter_settings) > 0:
                for filter_entity in filter_settings:
                    filter_entity.key.delete()
                self.response.write('Success')
            else:
                self.response.write('No matching filterSetting found')


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


class AddSharedProtocol(webapp2.RequestHandler):
    def post(self):
        if valid_secret_key(self.request):
            competition_parties = self.request.get('competitionParties')
            protocol_entity = SharedProtocol(parent=protocol_key(competition_parties))
            protocol_entity.competition_parties = competition_parties
            protocol_entity.put()
            self.response.write('Success')


class DeleteSharedProtocol(webapp2.RequestHandler):
    def post(self):
        if valid_secret_key(self.request):
            competition_parties = self.request.get('competitionParties')
            protocol_query = SharedProtocol.query(ancestor=protocol_key(competition_parties))
            protocols = protocol_query.fetch(100)
            if len(protocols) > 0:
                for protocol_entity in protocols:
                    protocol_entity.key.delete()
                self.response.write('Success')
            else:
                self.response.write('No matching protocol found')


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


class AddArticle(webapp2.RequestHandler):
    def post(self):
        if valid_secret_key(self.request):
            url = self.request.get('url')
            publisher = self.request.get('publisher')
            heading = self.request.get('heading')
            content = self.request.get('content')
            date = self.request.get('date')
            article_entity = Article(parent=article_key(url))
            article_entity.url = url
            article_entity.publisher = publisher
            article_entity.heading = heading
            article_entity.content = content
            article_entity.date = datetime.strptime(date, '%b %d %Y') # Jun 1 2005
            article_entity.put()
            self.response.write('Success')


app = webapp2.WSGIApplication([
    ('/', MainPage),
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
    ('/get_articles', GetArticles),
], debug=True)
