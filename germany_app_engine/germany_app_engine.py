import json
import webapp2
from google.appengine.ext import ndb
from competition_pages import SetSchedule, GetSchedule, SetCompetitions, GetCompetitions, SetTable, GetTable
from article_pages import AddArticle, GetArticle, GetArticles, ArticleExists, DeleteArticle
from analytics_pages import AddFilter, GetFilters, DeleteFilter, AddSharedProtocol, GetSharedProtocols, DeleteSharedProtocol
from server_utils import valid_secret_key

DEFAULT_TOKEN_VALUE = 'default_token'


def token_key(token_value=DEFAULT_TOKEN_VALUE):
    return ndb.Key('Token', token_value)


class Token(ndb.Model):
    """A GCM token to send the app users push notifications"""
    value = ndb.StringProperty(indexed=False)


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