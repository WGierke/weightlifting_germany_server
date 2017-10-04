import json

import webapp2
from analytics_pages import AddFilter, GetFilters, DeleteFilter, AddBlogFilter, GetBlogFilters, DeleteBlogFilter, AddSharedProtocol, GetSharedProtocols, DeleteSharedProtocol
from article_pages import AddArticle, GetArticle, GetArticles, ArticleExists, DeleteArticle
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from server_utils import get_secret_key, authenticated

DEFAULT_TOKEN_VALUE = 'default_token'
BULI_DATA_SERVER = 'http://weightliftingcompetitions.appspot.com'


def token_key(token_value=DEFAULT_TOKEN_VALUE):
    return ndb.Key('Token', token_value)


class Token(ndb.Model):
    """A GCM token to send the app users push notifications"""
    value = ndb.StringProperty(indexed=False)


class MainPage(webapp2.RequestHandler):
    @authenticated
    def get(self):
        self.response.out.write('Valid Secret Key - nice!')


class GetTokens(webapp2.RequestHandler):
    @authenticated
    def get(self):
        token_query = Token.query()
        tokens = token_query.fetch(1000)
        response_dict = {"result": map(lambda (x): x.value, tokens)}
        self.response.write(json.dumps(response_dict, encoding='latin1'))


class AddToken(webapp2.RequestHandler):
    @authenticated
    def post(self):
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


class DeleteToken(webapp2.RequestHandler):
    @authenticated
    def post(self):
        value = self.request.get('token')
        token_query = Token.query(ancestor=token_key(value))
        tokens = token_query.fetch(100)
        if len(tokens) > 0:
            for token in tokens:
                token.key.delete()
            self.response.write('Deleted token successfully')
        else:
            self.response.write('No token found')


class SetSchedule(webapp2.RequestHandler):
    def post(self):
        self.response.write(forward_post(self.request))


class GetSchedule(webapp2.RequestHandler):
    def get(self):
        self.response.write(forward_get(self.request))


class SetCompetitions(webapp2.RequestHandler):
    def post(self):
        self.response.write(forward_post(self.request))


class GetCompetitions(webapp2.RequestHandler):
    def get(self):
        self.response.write(forward_get(self.request))


class SetTable(webapp2.RequestHandler):
    def post(self):
        self.response.write(forward_post(self.request))


class GetTable(webapp2.RequestHandler):
    def get(self):
        self.response.write(forward_get(self.request))


@authenticated
def forward_get(request):
    return send_get(BULI_DATA_SERVER + request.path + "?" + request.query_string)


@authenticated
def forward_post(request):
    return send_post(request.body, BULI_DATA_SERVER + request.path)


def send_post(payload, url):
    headers = {'X-Secret-Key': get_secret_key()}
    result = urlfetch.fetch(
        url=url,
        payload=payload,
        method=urlfetch.POST,
        headers=headers)
    return result.content


def send_get(url):
    headers = {'X-Secret-Key': get_secret_key()}
    result = urlfetch.fetch(
        url=url,
        method=urlfetch.GET,
        headers=headers)
    return result.content


class GermanyServer():
    URL_MAPPING = [('/', MainPage),
                   ('/set_schedule', SetSchedule),
                   ('/get_schedule', GetSchedule),
                   ('/set_competitions', SetCompetitions),
                   ('/get_competitions', GetCompetitions),
                   ('/set_table', SetTable),
                   ('/get_table', GetTable),

                   ('/add_token', AddToken),
                   ('/delete_token', DeleteToken),
                   ('/get_tokens', GetTokens),

                   ('/add_filter', AddFilter),
                   ('/delete_filter', DeleteFilter),
                   ('/get_filters', GetFilters),

                   ('/add_blog_filter', AddBlogFilter),
                   ('/delete_blog_filter', DeleteBlogFilter),
                   ('/get_blog_filters', GetBlogFilters),

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
        return webapp2.WSGIApplication(self.URL_MAPPING, debug=False)


server = GermanyServer()
app = server.start()
